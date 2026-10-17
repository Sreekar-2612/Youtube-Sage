"""
FastAPI backend for YT-Sage.

This is the layer that turns our LangChain code into something a React
frontend can talk to over HTTP. All the LCEL/RAG/memory logic from src/
is unchanged from the core project -- only the delivery mechanism changed
from Streamlit to a JSON API.

Session model: each "Load video" call creates a session_id. That id maps to
an in-memory dict holding the retriever/chain/agent for that video, AND
(via src/chains.py's own session store) the conversational memory. The
React app just needs to hold onto the session_id string.
"""
import uuid
import os
import logging
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Load env variables using absolute path relative to main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
load_dotenv(dotenv_path=env_path, override=True)

from src.config import GROQ_MODEL_OPTIONS, HF_MODEL_OPTIONS
from src.youtube_loader import YouTubeTranscriptLoader
from src.text_processing import split_documents
from src.vectorstore import build_vectorstore, get_retriever, get_embeddings
from src.llm_setup import get_llm
from src.chains import build_conversational_chain, build_streaming_chain, clear_session_history, get_session_history
from src.agent_tools import build_agent
from langchain_core.documents import Document

app = FastAPI(title="YT-Sage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Pre-warm embedding model into RAM during container startup
    try:
        get_embeddings()
    except Exception as e:
        print("Embedding warm-up notice:", e)

# session_id -> {"retriever", "chain", "agent", "video_id"}
SESSIONS = {}


import urllib.request
import json
from src.youtube_loader import extract_video_id


def get_video_title(video_url: str) -> str:
    try:
        video_id = extract_video_id(video_url)
        url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            return data.get("title", f"Video {video_id}")
    except Exception:
        return "Loaded YouTube Stream"


def generate_video_overview(llm, title: str, chunks: List[Document]) -> tuple[str, List[str]]:
    """Generates an instant executive summary and 3 suggested questions on video load."""
    if not chunks:
        return (
            "General chat session active.",
            ["What can you help me with?", "Explain RAG architecture", "How to use this tool?"]
        )

    context_sample = "\n\n".join(c.page_content[:250] for c in chunks[:3])
    prompt = (
        f"You are analyzing a YouTube video titled '{title}'.\n"
        f"Transcript excerpt:\n{context_sample}\n\n"
        "Provide:\n"
        "1. A 2-bullet concise executive summary (markdown format).\n"
        "2. Exactly 3 short, intriguing questions a viewer should ask about this video.\n"
        "Respond ONLY in valid JSON matching this schema:\n"
        "{\n"
        "  \"summary\": \"- Key point 1\\n- Key point 2\",\n"
        "  \"suggested_questions\": [\"Question 1?\", \"Question 2?\", \"Question 3?\"]\n"
        "}"
    )
    try:
        raw = llm.invoke(prompt).content
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
        data = json.loads(cleaned)
        return (
            data.get("summary", f"Loaded '{title}' with {len(chunks)} indexed segments."),
            data.get("suggested_questions", [
                "Summarize the key takeaways of this video",
                "What tools or concepts are discussed?",
                "What is the conclusion or next step?"
            ])
        )
    except Exception as e:
        logger.warning(f"Overview generation fallback: {e}")
        return (
            f"Video '{title}' indexed with {len(chunks)} timestamped segments.",
            [
                "Summarize the main takeaways",
                "What are the most important insights discussed?",
                "List all key concepts mentioned"
            ]
        )


class LoadVideoRequest(BaseModel):
    video_url: str
    provider: str = "groq"          # "groq" | "huggingface"
    model_name: str


class LoadVideoResponse(BaseModel):
    session_id: str
    video_id: str
    num_chunks: int
    title: str
    summary: Optional[str] = None
    suggested_questions: List[str] = []


class ChatRequest(BaseModel):
    session_id: str
    question: str
    use_agent: bool = False


class ChatResponse(BaseModel):
    answer: str
    key_points: List[str] = []
    confidence: Optional[str] = None


class ClearRequest(BaseModel):
    session_id: str


class GoogleAuthRequest(BaseModel):
    id_token: str


@app.get("/api/config")
def get_config():
    """Lets the frontend populate provider/model dropdowns without hardcoding them."""
    return {
        "groq_models": GROQ_MODEL_OPTIONS,
        "hf_models": HF_MODEL_OPTIONS,
        "google_client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
    }


@app.post("/api/auth/google")
def google_auth(req: GoogleAuthRequest):
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not client_id:
            raise HTTPException(status_code=500, detail="Google Client ID not configured.")
        # Verify OAuth token
        idinfo = id_token.verify_oauth2_token(req.id_token, google_requests.Request(), client_id)
        
        # Extract validated user profile details
        userid = idinfo['sub']
        email = idinfo.get('email')
        name = idinfo.get('name')
        picture = idinfo.get('picture')
        
        return {
            "email": email,
            "name": name,
            "picture": picture,
            "userid": userid
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google ID Token: {str(e)}")


@app.post("/api/session/load", response_model=LoadVideoResponse)
def load_video(req: LoadVideoRequest):
    logger.info(f"Loading video: {req.video_url} (provider={req.provider}, model={req.model_name})")
    try:
        if req.video_url == "temp-chat":
            docs = [Document(page_content="Temporary general chat session. You can ask anything.", metadata={"video_id": "temp-chat", "source": "temp-chat"})]
            chunks = docs
            vectorstore = build_vectorstore(chunks)
            retriever = get_retriever(vectorstore, chunks)
            llm = get_llm(req.provider, req.model_name)
            session_id = str(uuid.uuid4())
            title = "Temporary Chat"
            
            SESSIONS[session_id] = {
                "retriever": retriever,
                "chain": build_conversational_chain(llm, retriever),
                "stream_chain": build_streaming_chain(llm, retriever),
                "agent": build_agent(llm, retriever),
                "video_id": "temp-chat",
                "title": title,
            }
            return LoadVideoResponse(
                session_id=session_id,
                video_id="temp-chat",
                num_chunks=0,
                title=title,
                summary="Temporary general chat session. You can ask anything without video indexing.",
                suggested_questions=[
                    "How does RAG retrieval work?",
                    "What makes Groq LPU inference fast?",
                    "How do timestamped video citations work?"
                ]
            )

        loader = YouTubeTranscriptLoader(req.video_url)
        docs = loader.load()
        chunks = split_documents(docs)
        vectorstore = build_vectorstore(chunks)
        # Pass chunks to initialize HybridRetriever (Dense FAISS + BM25 keyword matching)
        retriever = get_retriever(vectorstore, chunks)

        llm = get_llm(req.provider, req.model_name)

        session_id = str(uuid.uuid4())
        
        # Get video title
        title = get_video_title(req.video_url)

        # Generate instant executive summary and suggested questions
        summary, suggested_questions = generate_video_overview(llm, title, chunks)

        SESSIONS[session_id] = {
            "retriever": retriever,
            "chain": build_conversational_chain(llm, retriever),
            "stream_chain": build_streaming_chain(llm, retriever),
            "agent": build_agent(llm, retriever),
            "video_id": docs[0].metadata["video_id"],
            "title": title,
            "summary": summary,
            "suggested_questions": suggested_questions,
        }

        return LoadVideoResponse(
            session_id=session_id,
            video_id=docs[0].metadata["video_id"],
            num_chunks=len(chunks),
            title=title,
            summary=summary,
            suggested_questions=suggested_questions,
        )
    except Exception as e:
        logger.error(f"Failed to load video: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session = SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Load a video first.")

    try:
        if req.use_agent:
            history = get_session_history(req.session_id)
            result = session["agent"].invoke(
                {"question": req.question, "chat_history": history.messages}
            )
            history.add_user_message(req.question)
            history.add_ai_message(result["output"])
            return ChatResponse(answer=result["output"])

        result = session["chain"].invoke(
            {"question": req.question},
            config={"configurable": {"session_id": req.session_id}},
        )
        return ChatResponse(
            answer=result.answer,
            key_points=result.key_points,
            confidence=result.confidence,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    session = SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Load a video first.")

    async def event_generator():
        try:
            stream_chain = session.get("stream_chain")
            if not stream_chain:
                llm = get_llm("groq", "llama-3.1-8b-instant")
                stream_chain = build_streaming_chain(llm, session["retriever"])
                session["stream_chain"] = stream_chain

            # Stream tokens in real-time from the LCEL chain
            async for token in stream_chain.astream(
                {"question": req.question},
                config={"configurable": {"session_id": req.session_id}}
            ):
                if token:
                    data = json.dumps({"token": token})
                    yield f"data: {data}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as err:
            logger.error(f"Error during stream generation: {err}")
            err_data = json.dumps({"error": str(err)})
            yield f"data: {err_data}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/session/clear")
def clear_session(req: ClearRequest):
    clear_session_history(req.session_id)
    return {"status": "cleared"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
import uuid
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import GROQ_MODEL_OPTIONS, HF_MODEL_OPTIONS
from src.youtube_loader import YoutubeTranscriptLoader
from src.text_processing import split_documents
from src.vectorstore import build_vectorstore, get_retriever
from src.llm_setup import get_llm
from src.chains import build_conversational_chains, clear_session_history
from src.agent_tools import build_agent


app = FastAPI(title = "YT-Sage API")

# middleware is the code that sits between the incoming request and the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# session_id -> {"retriever", "chain", "agent", "video_id"}
sessions = {}

# data coming to the backend
class LoadVideoRequest(BaseModel):
    video_url:str
    provider:str = "groq"
    model_name:str

# data going back to the frontend
# session_id → Which chat conversation does this belong to?
# video_id   → Which YouTube video was processed?
# num_chunks → How many transcript chunks were created?
class LoadVideoResponse(BaseModel):
    session_id:str
    video_id:str
    num_chunks:int 

class ChatRequest(BaseModel):
    session_id:str
    question:str
    use_agent:bool = False

class ChatResponse(BaseModel):
    answer:str
    key_points:List[str] = []
    confidence: Optional[str] = None

class ClearRequest(BaseModel):
    session_id : str

@app.get("/api/config")
def get_config():
    # lets the frontenfd populate provider/model dropdowns without hardcoding them
    return {
        "groq_models":GROQ_MODEL_OPTIONS,
        "hf_models":HF_MODEL_OPTIONS
    }

@app.post("/api/session/load", response_model = LoadVideoResponse)
def load_video(req:LoadVideoRequest):
    try:
        loader = YoutubeTranscriptLoader(req.video_url)
        docs = loader.load()
        chunks = split_documents(docs)
        vectorstore = build_vectorstore(chunks)
        retriever = get_retriever(vectorstore)

        llm = get_llm(req.provider,req.model_name)

        session-id = str(uuid.uuid4())
        SESSIONS[session_id] = {
            "retriever":retriever,
            "chain":build_conversational_chain(llm,retriever)
            "agent":build_agent(llm,retriever)
            "video_id":docs[0].,etadata["video_id"],
        }
        
        return LoadVideoResponse(
            session_id = session_id,
            video_id = docs[0].metadata["video_id"],
            num_chunks = len(chunks)
        )
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(a))
    

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session = SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Load a video first.")

    try:
        if req.use_agent:
            result = session["agent"].invoke(
                {"question": req.question, "chat_history": []}
            )
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


@app.post("/api/session/clear")
def clear_session(req: ClearRequest):
    clear_session_history(req.session_id)
    return {"status": "cleared"}


@app.get("/api/health")
def health():
    return {"status": "ok"}   
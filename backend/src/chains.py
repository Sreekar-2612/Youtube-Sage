from typing import List
from operator import itemgetter

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda,
    RunnableBranch,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from pydantic import BaseModel, Field

class VideoAnswer(BaseModel):
    answer : str = Field(
        description = "A direct , well-formed , professional answer to the user's question"
    )
    key_points: List[str] = Field(
        description = "5-6 short bullet point summarizing the answer",
        default_factory = list
    )
    confidence : str = Field(
        description = "One of : high , medium , low- how well the transcript supports this answer"
    )


structured_parser = PydanticOutputParser(
    pydantic_object = VideoAnswer
)

# format the returned docs
# we need single string 
def format_docs(docs: List[Document]) ->str:
    return "\n\n".join(f"[Segment {i+1}]\n{d.page_content}" for i , d in enumerate(docs))


format_docs_runnable = RunnableLambda(format_docs)


# Query condensatio chain

def build_condense_chain(llm):
    condense_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system" , "Rewrtie the latest user question as a standalone question, "
                           "using the chat history for context. Return ONLY the rewrittenr question , nothing else"
            ),
            MessagesPlaceholder("chat_history"),
            ("human","{question}"),
        ]
    )
    
    has_history = lambda x : len(x.get("chat_history", [])) > 0

    condense_chain = RunnableBranch(
        (has_history, condense_prompt | llm | StrOutputParser()),
        itemgetter("question"), # if no history -> then pass through the question unchanged
    )
    return condense_chain

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are YT-Sage, an assistant that answers question about a Youtube"
            "video using ONLY the transcript context provided below. If the answer"
            "isn't in the context , say honestly instead of making things up.\n\n"
            "Transcript context : \n{context}\n\n"
            "Respond in this exact JSON format: \n{format_instructions}"
        ),
        MessagesPlaceholder("chat_history"),
        ("human","{question}"),
    ]
).partial(format_instructions = structured_parser.get_format_instructions())

def build_rag_chain(llm, retriever):
    condense_chain = build_condense_chain(llm)

    chain = (
        RunnableParallel(
            {
                "standalone_question":condense_chain,
                "question":itemgetter("question"),
                "chat_history":itemgetter("chat_history")
            }
        )
        | RunnableParallel(
            {
                "context":itemgetter("standalone_question") | retriever | format_docs_runnable,
                "question": itemgetter("question"),
                "chat_history":itemgetter("chat_history"),
            }
        )
        | ANSWER_PROMPT | llm | structured_parser
    )
    return chain

# chat memory

_session_store = {}

def get_session_history(session_id : str) -> ChatMessageHistory:
    if session_id not in _session_store:
        _session_store[session_id] = ChatMessageHistory()
    return _session_store[session_id]

def build_conversational_chain(llm, retriever):
    rag_chain = build_rag_chain(llm , retriever)
    return RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key = "question",
        history_messages_key = "chat_history",
    )

def clear_session_history(session_id: str):
    _session_store.pop(session_id,None)
    
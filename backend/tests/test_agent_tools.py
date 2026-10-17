"""
QA Test Suite for Subagent 2: Review of Track 1 (Upgraded Agent Tools)
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.documents import Document
from src.vectorstore import build_vectorstore, get_retriever
from src.llm_setup import get_llm
from src.agent_tools import build_agent

def test_agent_tools():
    print("[TEST 1] Testing Agent Tool Suite Initialization...")
    docs = [
        Document(page_content="[00:10] In this video we explore FastAPI and Python web development.", metadata={"timestamp": "00:10", "start_seconds": 10.0}),
        Document(page_content="[02:30] Use pip install langchain to set up your RAG project.", metadata={"timestamp": "02:30", "start_seconds": 150.0}),
        Document(page_content="[05:00] In conclusion, vector search and LLMs enable powerful agents.", metadata={"timestamp": "05:00", "start_seconds": 300.0}),
    ]
    vectorstore = build_vectorstore(docs)
    retriever = get_retriever(vectorstore, docs)
    llm = get_llm("groq", "llama-3.1-8b-instant")
    
    agent_executor = build_agent(llm, retriever)
    assert agent_executor is not None, "AgentExecutor should be initialized"
    
    # Inspect tools in agent
    tool_names = [t.name for t in agent_executor.tools]
    print(f"  -> Bound tools: {tool_names}")
    expected_tools = ["search_transcript", "generate_video_chapters", "generate_study_quiz", "extract_code_or_tools"]
    for exp in expected_tools:
        assert exp in tool_names, f"Expected tool {exp} not bound to agent"
    print("  -> PASS: All 4 advanced agent tools successfully bound.")

def test_chapter_and_code_tool_invocations():
    print("[TEST 2] Testing Tool Direct Invocations...")
    docs = [
        Document(page_content="[01:00] Setting up Docker containers with docker-compose up.", metadata={"timestamp": "01:00", "start_seconds": 60.0}),
    ]
    vectorstore = build_vectorstore(docs)
    retriever = get_retriever(vectorstore, docs)
    llm = get_llm("groq", "llama-3.1-8b-instant")
    agent_executor = build_agent(llm, retriever)
    
    tools_dict = {t.name: t for t in agent_executor.tools}
    chapters_out = tools_dict["generate_video_chapters"].invoke({"topic": "Docker"})
    assert "[01:00]" in chapters_out, f"Expected [01:00] in chapter output: {chapters_out}"
    print(f"  -> Chapter output verified: {chapters_out.strip()}")
    
    code_out = tools_dict["extract_code_or_tools"].invoke({"topic": "Docker"})
    assert "docker-compose" in code_out, f"Expected docker-compose in code output: {code_out}"
    print(f"  -> Code extraction verified: {code_out.strip()}")
    print("  -> PASS: Tool invocations return high-signal context.")

if __name__ == "__main__":
    test_agent_tools()
    test_chapter_and_code_tool_invocations()
    print("\n=== ALL SUBAGENT 2 QA REVIEWS PASSED (2/2) ===")

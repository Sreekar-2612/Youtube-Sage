"""
QA Test Suite for Subagent 4: Review of Task 2 (Hybrid Retrieval & Streaming Engine)
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.documents import Document
from src.vectorstore import build_vectorstore, get_retriever, BM25KeywordRetriever, HybridRetriever
from src.llm_setup import get_llm
from src.chains import build_streaming_chain

def test_bm25_keyword_retriever():
    print("[TEST 1] Testing BM25KeywordRetriever...")
    docs = [
        Document(page_content="Python FastAPI is high-performance web framework for APIs.", metadata={"id": 1}),
        Document(page_content="React is a declarative library for user interfaces.", metadata={"id": 2}),
        Document(page_content="LangChain simplifies building LLM and RAG pipelines.", metadata={"id": 3}),
        Document(page_content="FAISS provides fast vector similarity search.", metadata={"id": 4}),
    ]
    bm25 = BM25KeywordRetriever.from_documents(docs)
    results = bm25.invoke("FastAPI web framework")
    assert len(results) > 0, "BM25 should return relevant documents"
    assert results[0].metadata["id"] == 1, f"Expected doc 1 for FastAPI query, got {results[0].metadata['id']}"
    print(f"  -> PASS: BM25 matched '{results[0].page_content[:35]}...'")

def test_hybrid_retriever_rrf():
    print("[TEST 2] Testing HybridRetriever (Dense FAISS + BM25 Reciprocal Rank Fusion)...")
    docs = [
        Document(page_content="[00:15] Deep learning models process embeddings for semantics.", metadata={"start_seconds": 15.0}),
        Document(page_content="[01:30] Docker and containerization ensure reliable deployments.", metadata={"start_seconds": 90.0}),
        Document(page_content="[02:45] Hybrid search merges keyword BM25 with vector search.", metadata={"start_seconds": 165.0}),
    ]
    vectorstore = build_vectorstore(docs)
    hybrid = get_retriever(vectorstore, docs)
    assert isinstance(hybrid, HybridRetriever), f"Expected HybridRetriever, got {type(hybrid)}"
    
    # Query with exact keyword
    results = hybrid.invoke("Docker deployment")
    assert len(results) > 0, "Hybrid retriever should return documents"
    assert results[0].metadata["start_seconds"] == 90.0, f"Expected doc with 90s, got {results[0].metadata}"
    print(f"  -> PASS: HybridRetriever retrieved '{results[0].page_content}' as top match.")

def test_streaming_chain_construction():
    print("[TEST 3] Testing build_streaming_chain...")
    docs = [Document(page_content="[00:00] Overview of LangChain LCEL architecture.", metadata={"start_seconds": 0.0})]
    vectorstore = build_vectorstore(docs)
    retriever = get_retriever(vectorstore, docs)
    llm = get_llm("groq", "llama-3.1-8b-instant")
    chain = build_streaming_chain(llm, retriever)
    assert chain is not None, "Streaming chain should be created successfully"
    print("  -> PASS: Streaming chain initialized with LCEL RunnableWithMessageHistory.")

if __name__ == "__main__":
    test_bm25_keyword_retriever()
    test_hybrid_retriever_rrf()
    test_streaming_chain_construction()
    print("\n=== ALL SUBAGENT 4 QA REVIEWS PASSED (3/3) ===")

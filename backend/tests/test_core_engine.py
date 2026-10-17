"""
QA Test Suite for Subagent 2: Review of Task 1 (Core Engine, Models, Embeddings & Timestamp Chunker)
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import GROQ_MODEL_OPTIONS, EMBEDDING_MODEL
from src.vectorstore import get_embeddings
from src.text_processing import split_documents
from langchain_core.documents import Document

def test_groq_models():
    print("[TEST 1] Verifying GROQ_MODEL_OPTIONS...")
    valid_expected = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "deepseek-r1-distill-llama-70b", "gemma2-9b-it", "mixtral-8x7b-32768"]
    configured_ids = list(GROQ_MODEL_OPTIONS.values())
    for exp in valid_expected:
        assert exp in configured_ids, f"Expected model {exp} missing from GROQ_MODEL_OPTIONS"
    print("  -> PASS: All production Groq models present.")

def test_embeddings():
    print("[TEST 2] Verifying Real Semantic Embeddings...")
    emb = get_embeddings()
    emb_type = type(emb).__name__
    print(f"  -> Embeddings instance: {emb_type}")
    assert "HuggingFace" in emb_type or "SentenceTransformer" in emb_type, f"Expected real embeddings, got {emb_type}"
    vector = emb.embed_query("Hello world test query")
    assert len(vector) == 384, f"Expected 384 dimensions for all-MiniLM-L6-v2, got {len(vector)}"
    print(f"  -> PASS: Embeddings produced valid 384-dim dense vector.")

def test_timestamp_preserving_chunker():
    print("[TEST 3] Verifying Timestamp-Preserving Chunker...")
    sample_segments = [
        {"text": "Welcome to this tutorial on LangChain and RAG.", "start": 0.0, "duration": 5.0},
        {"text": "Today we will explore vector databases and semantic search.", "start": 5.5, "duration": 6.0},
        {"text": "Let us begin by loading the YouTube transcript.", "start": 70.0, "duration": 5.0},
        {"text": "Next we chunk the subtitles while retaining the timestamps.", "start": 80.0, "duration": 8.0},
        {"text": "Notice how each chunk records start and end times.", "start": 160.0, "duration": 6.0},
    ]
    doc = Document(
        page_content="Welcome to this tutorial on LangChain and RAG. Today we will explore vector databases and semantic search.",
        metadata={
            "source": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "video_id": "dQw4w9WgXcQ",
            "segments": sample_segments
        }
    )
    chunks = split_documents([doc])
    assert len(chunks) >= 2, f"Expected at least 2 time-window chunks, got {len(chunks)}"
    for idx, c in enumerate(chunks):
        assert "timestamp" in c.metadata, f"Chunk {idx} missing 'timestamp' in metadata"
        assert "start_seconds" in c.metadata, f"Chunk {idx} missing 'start_seconds'"
        assert c.page_content.startswith(f"[{c.metadata['timestamp']}]"), f"Chunk text should start with [{c.metadata['timestamp']}]"
        print(f"  -> Chunk {idx + 1}: ts={c.metadata['timestamp']} ({c.metadata['start_seconds']}s - {c.metadata['end_seconds']}s): {c.page_content[:45]}...")
    print("  -> PASS: All chunks correctly preserve timestamp metadata and prefix.")

if __name__ == "__main__":
    test_groq_models()
    test_embeddings()
    test_timestamp_preserving_chunker()
    print("\n=== ALL SUBAGENT 2 QA REVIEWS PASSED (3/3) ===")

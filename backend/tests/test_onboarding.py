"""
QA Test Suite for Subagent 4: Review of Track 2 (Instant Video Onboarding & Quick-Prompt Starters)
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.documents import Document
from main import LoadVideoResponse, generate_video_overview
from src.llm_setup import get_llm

def test_load_video_response_schema():
    print("[TEST 1] Testing LoadVideoResponse Schema...")
    res = LoadVideoResponse(
        session_id="test-session-123",
        video_id="abc123xyz",
        num_chunks=15,
        title="LangChain Tutorial",
        summary="- Key point 1\n- Key point 2",
        suggested_questions=["What is LangChain?", "How to use RAG?"]
    )
    assert res.summary is not None, "Summary should be present"
    assert len(res.suggested_questions) == 2, "Suggested questions count should match"
    print("  -> PASS: LoadVideoResponse schema validation successful.")

def test_generate_video_overview_fallback():
    print("[TEST 2] Testing generate_video_overview fallback safety...")
    # Empty chunks scenario
    summary, questions = generate_video_overview(None, "Test Video", [])
    assert len(questions) == 3, f"Expected 3 fallback questions, got {len(questions)}"
    assert "General chat session" in summary
    print(f"  -> PASS: Fallback summary: {summary}")
    print(f"  -> PASS: Fallback questions: {questions}")

if __name__ == "__main__":
    test_load_video_response_schema()
    test_generate_video_overview_fallback()
    print("\n=== ALL SUBAGENT 4 QA REVIEWS PASSED (2/2) ===")

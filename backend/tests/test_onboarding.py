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

def test_generate_video_overview_with_mock_llm():
    print("[TEST 3] Testing generate_video_overview regex parsing with mock LLM...")
    class MockLLMResponse:
        def __init__(self, content):
            self.content = content

    class MockLLM:
        def invoke(self, prompt):
            return MockLLMResponse(
                '```json\n{"summary": "- Deep learning overview\\n- RAG architecture", "suggested_questions": ["What is RAG?", "How does MiniLM work?", "Why use hybrid search?"]}\n```'
            )

    chunks = [Document(page_content="Sample transcript chunk", metadata={})]
    summary, questions = generate_video_overview(MockLLM(), "Test Video", chunks)
    assert "- Deep learning overview" in summary, f"Expected parsed summary, got {summary}"
    assert len(questions) == 3, f"Expected 3 questions, got {len(questions)}"
    assert questions[0] == "What is RAG?"
    print("  -> PASS: Mock LLM output parsed successfully without NameError on 're'.")

def test_session_eviction():
    print("[TEST 4] Testing store_session memory eviction...")
    from main import store_session, SESSIONS, MAX_SESSIONS
    for i in range(MAX_SESSIONS + 5):
        store_session(f"session-{i}", {"data": i})
    assert len(SESSIONS) == MAX_SESSIONS, f"Expected {MAX_SESSIONS} sessions, got {len(SESSIONS)}"
    assert "session-0" not in SESSIONS, "Oldest session session-0 should have been evicted"
    assert f"session-{MAX_SESSIONS + 4}" in SESSIONS, "Latest session should be in SESSIONS"
    print(f"  -> PASS: LRU eviction successfully capped SESSIONS at {MAX_SESSIONS}.")

if __name__ == "__main__":
    test_load_video_response_schema()
    test_generate_video_overview_fallback()
    test_generate_video_overview_with_mock_llm()
    test_session_eviction()
    print("\n=== ALL SUBAGENT 4 QA REVIEWS PASSED (4/4) ===")

"""
Integration Smoke Test Suite:
Validates FastAPI endpoints end-to-end using TestClient.
"""
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

def run_integration_tests():
    client = TestClient(app)

    print("[INTEGRATION 1] Testing /api/health...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert res.json() == {"status": "ok"}
    print("  -> PASS /api/health")

    print("[INTEGRATION 2] Testing /api/config...")
    res = client.get("/api/config")
    assert res.status_code == 200
    data = res.json()
    assert "groq_models" in data
    assert "hf_models" in data
    print("  -> PASS /api/config: models verified")

    print("[INTEGRATION 3] Testing /api/session/load with temp-chat...")
    res = client.post("/api/session/load", json={
        "video_url": "temp-chat",
        "provider": "groq",
        "model_name": "llama-3.1-8b-instant"
    })
    assert res.status_code == 200, f"Failed load: {res.text}"
    session_data = res.json()
    session_id = session_data["session_id"]
    assert session_id is not None
    assert len(session_data["suggested_questions"]) == 3
    print(f"  -> PASS /api/session/load: session_id={session_id[:8]}... questions count={len(session_data['suggested_questions'])}")

    print("[INTEGRATION 4] Testing /api/chat/stream with temp-chat session...")
    stream_res = client.post("/api/chat/stream", json={
        "session_id": session_id,
        "question": "What is this tool?",
        "use_agent": False
    })
    assert stream_res.status_code == 200, f"Stream failed: {stream_res.text}"
    tokens = []
    for line in stream_res.iter_lines():
        if line.startswith("data: "):
            payload = line[6:]
            if payload == "[DONE]":
                break
            try:
                parsed = json.loads(payload)
                if "token" in parsed:
                    tokens.append(parsed["token"])
            except Exception:
                pass
    full_text = "".join(tokens)
    print(f"  -> PASS /api/chat/stream: received {len(tokens)} token events ({len(full_text)} chars)")

    print("[INTEGRATION 5] Testing /api/session/clear...")
    clear_res = client.post("/api/session/clear", json={"session_id": session_id})
    assert clear_res.status_code == 200
    assert clear_res.json() == {"status": "cleared"}
    print("  -> PASS /api/session/clear")

    print("\n" + "=" * 60)
    print("[OK] ALL INTEGRATION SMOKE TESTS PASSED (5/5)")
    print("=" * 60)

if __name__ == "__main__":
    run_integration_tests()

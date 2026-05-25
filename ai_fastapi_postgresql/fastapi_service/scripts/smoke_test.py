import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


client = TestClient(app)


def main() -> None:
    health = client.get("/health")
    assert health.status_code == 200, health.text
    assert health.json()["status"] == "ok"

    payload = {
        "corpus_item_id": "33333333-3333-3333-3333-333333333335",
        "corpus_type": "sentence",
        "hanzi": "我想学习中文。",
        "pinyin": "wǒ xiǎng xué xí zhōng wén.",
        "duration_ms": 2800,
    }
    response = client.post("/api/v1/pronunciation/evaluate", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["model_version"] == "mock-v1"
    assert data["overall_score"] > 0
    audio_response = client.post(
        "/api/v1/audio/analyze",
        files={"audio": ("sample.wav", _make_wav(), "audio/wav")},
    )
    assert audio_response.status_code == 200, audio_response.text
    assert audio_response.json()["analysis"]["duration_ms"] > 0
    print("FastAPI smoke test passed:", data["overall_score"])


def _make_wav() -> bytes:
    import io
    import wave

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b"\x00\x00" * 16000)
    return buffer.getvalue()


if __name__ == "__main__":
    main()

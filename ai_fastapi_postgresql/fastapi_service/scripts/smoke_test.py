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
    assert data["model_version"] == "duration-rule-v1"
    assert data["overall_score"] > 0
    audio_response = client.post(
        "/api/v1/audio/analyze",
        files={"audio": ("sample.wav", _make_wav(), "audio/wav")},
    )
    assert audio_response.status_code == 200, audio_response.text
    assert audio_response.json()["analysis"]["duration_ms"] > 0
    model_response = client.post(
        "/api/v1/pronunciation/evaluate-audio",
        data={
            "corpus_type": "sentence",
            "hanzi": "我想学习中文。",
            "pinyin": "wǒ xiǎng xué xí zhōng wén.",
        },
        files={"audio": ("sample.wav", _make_wav(), "audio/wav")},
    )
    assert model_response.status_code == 200, model_response.text
    model_data = model_response.json()
    assert model_data["model_version"] == "tone-align-calibrated-v1"
    assert model_data["audio_features"]["duration_ms"] > 0
    assert len(model_data["syllable_analysis"]) == 6
    assert model_data["syllable_analysis"][0]["alignment_method"] == "energy-valley-v1"
    versions_response = client.get("/api/v1/model/versions")
    assert versions_response.status_code == 200, versions_response.text
    assert any(item["version_code"] == "tone-align-calibrated-v1" for item in versions_response.json()["items"])
    print("FastAPI smoke test passed:", data["overall_score"])


def _make_wav() -> bytes:
    import io
    import math
    import struct
    import wave

    sample_rate = 16000
    duration_seconds = 2
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        frames = bytearray()
        for index in range(sample_rate * duration_seconds):
            frequency = 180 + 45 * (index / (sample_rate * duration_seconds))
            sample = round(math.sin((2 * math.pi * frequency * index) / sample_rate) * 9000)
            frames.extend(struct.pack("<h", sample))
        wav_file.writeframes(bytes(frames))
    return buffer.getvalue()


if __name__ == "__main__":
    main()

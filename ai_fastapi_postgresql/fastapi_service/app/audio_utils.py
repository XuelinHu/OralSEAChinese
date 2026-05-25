import io
import wave


def analyze_wav_duration(content: bytes) -> dict[str, int | float | str]:
    try:
        with wave.open(io.BytesIO(content), "rb") as wav_file:
            frame_count = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            duration_ms = round(frame_count / sample_rate * 1000) if sample_rate else 0
            return {
                "format": "wav",
                "duration_ms": duration_ms,
                "sample_rate": sample_rate,
                "channels": channels,
                "frame_count": frame_count,
            }
    except wave.Error:
        return {
            "format": "unknown",
            "duration_ms": 0,
            "sample_rate": 0,
            "channels": 0,
            "frame_count": 0,
        }

import io
import math
import struct
import wave
from typing import TypedDict


class WavSignal(TypedDict):
    format: str
    duration_ms: int
    sample_rate: int
    channels: int
    frame_count: int
    samples: list[float]


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


def analyze_wav_features(content: bytes, frame_ms: int = 25) -> dict[str, int | float | str]:
    signal = read_wav_signal(content)
    if signal["format"] == "unknown":
        return {
            "format": "unknown",
            "duration_ms": 0,
            "sample_rate": 0,
            "channels": 0,
            "rms": 0.0,
            "peak": 0.0,
            "voiced_ratio": 0.0,
            "silence_ratio": 1.0,
            "longest_silence_ms": 0,
            "energy_variation": 0.0,
        }

    samples = signal["samples"]
    duration_ms = signal["duration_ms"]
    sample_rate = signal["sample_rate"]
    channels = signal["channels"]
    if not samples:
        return {
            "format": "wav",
            "duration_ms": duration_ms,
            "sample_rate": sample_rate,
            "channels": channels,
            "rms": 0.0,
            "peak": 0.0,
            "voiced_ratio": 0.0,
            "silence_ratio": 1.0,
            "longest_silence_ms": duration_ms,
            "energy_variation": 0.0,
        }

    peak = max(abs(sample) for sample in samples)
    rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples))
    frame_size = max(1, round(sample_rate * frame_ms / 1000))
    frame_energies = []
    for index in range(0, len(samples), frame_size):
        frame = samples[index : index + frame_size]
        if not frame:
            continue
        frame_energies.append(math.sqrt(sum(sample * sample for sample in frame) / len(frame)))

    speech_threshold = max(0.015, rms * 0.45)
    voiced_frames = [energy for energy in frame_energies if energy >= speech_threshold]
    voiced_ratio = len(voiced_frames) / len(frame_energies) if frame_energies else 0.0
    silence_ratio = 1.0 - voiced_ratio
    longest_silence_frames = _longest_run([energy < speech_threshold for energy in frame_energies])
    longest_silence_ms = longest_silence_frames * frame_ms
    mean_energy = sum(frame_energies) / len(frame_energies) if frame_energies else 0.0
    energy_variation = (
        math.sqrt(sum((energy - mean_energy) ** 2 for energy in frame_energies) / len(frame_energies)) / mean_energy
        if mean_energy > 0
        else 0.0
    )

    return {
        "format": "wav",
        "duration_ms": duration_ms,
        "sample_rate": sample_rate,
        "channels": channels,
        "rms": round(rms, 5),
        "peak": round(peak, 5),
        "voiced_ratio": round(voiced_ratio, 4),
        "silence_ratio": round(silence_ratio, 4),
        "longest_silence_ms": longest_silence_ms,
        "energy_variation": round(energy_variation, 4),
    }


def read_wav_signal(content: bytes) -> WavSignal:
    try:
        with wave.open(io.BytesIO(content), "rb") as wav_file:
            frame_count = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            raw = wav_file.readframes(frame_count)
    except wave.Error:
        return {
            "format": "unknown",
            "duration_ms": 0,
            "sample_rate": 0,
            "channels": 0,
            "frame_count": 0,
            "samples": [],
        }

    return {
        "format": "wav",
        "duration_ms": round(frame_count / sample_rate * 1000) if sample_rate else 0,
        "sample_rate": sample_rate,
        "channels": channels,
        "frame_count": frame_count,
        "samples": _decode_pcm(raw, sample_width, channels),
    }


def estimate_pitch_track(
    samples: list[float],
    sample_rate: int,
    frame_ms: int = 40,
    hop_ms: int = 20,
    min_f0: int = 75,
    max_f0: int = 450,
) -> list[dict[str, float | int]]:
    if not samples or sample_rate <= 0:
        return []

    frame_size = max(1, round(sample_rate * frame_ms / 1000))
    hop_size = max(1, round(sample_rate * hop_ms / 1000))
    min_lag = max(1, sample_rate // max_f0)
    max_lag = max(min_lag + 1, sample_rate // min_f0)
    track: list[dict[str, float | int]] = []

    for start in range(0, max(1, len(samples) - frame_size + 1), hop_size):
        frame = samples[start : start + frame_size]
        if len(frame) < frame_size // 2:
            continue
        f0, confidence = _estimate_frame_f0(frame, sample_rate, min_lag, max_lag)
        track.append(
            {
                "time_ms": round((start + len(frame) / 2) / sample_rate * 1000),
                "f0_hz": round(f0, 2),
                "confidence": round(confidence, 4),
            }
        )
    return track


def _estimate_frame_f0(frame: list[float], sample_rate: int, min_lag: int, max_lag: int) -> tuple[float, float]:
    mean = sum(frame) / len(frame)
    centered = [sample - mean for sample in frame]
    energy = sum(sample * sample for sample in centered)
    if energy <= 1e-6:
        return 0.0, 0.0

    best_lag = 0
    best_score = 0.0
    upper_lag = min(max_lag, len(centered) - 2)
    for lag in range(min_lag, upper_lag + 1):
        left = centered[:-lag]
        right = centered[lag:]
        left_energy = sum(sample * sample for sample in left)
        right_energy = sum(sample * sample for sample in right)
        if left_energy <= 1e-9 or right_energy <= 1e-9:
            continue
        score = sum(first * second for first, second in zip(left, right)) / math.sqrt(left_energy * right_energy)
        if score > best_score:
            best_score = score
            best_lag = lag

    if best_lag <= 0 or best_score < 0.35:
        return 0.0, max(0.0, best_score)
    return sample_rate / best_lag, best_score


def _decode_pcm(raw: bytes, sample_width: int, channels: int) -> list[float]:
    if sample_width != 2:
        return []
    sample_count = len(raw) // 2
    if sample_count <= 0:
        return []
    values = struct.unpack("<" + "h" * sample_count, raw)
    if channels <= 1:
        return [value / 32768.0 for value in values]

    mono = []
    for index in range(0, len(values), channels):
        frame = values[index : index + channels]
        mono.append(sum(frame) / len(frame) / 32768.0)
    return mono


def _longest_run(values: list[bool]) -> int:
    longest = 0
    current = 0
    for value in values:
        if value:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest

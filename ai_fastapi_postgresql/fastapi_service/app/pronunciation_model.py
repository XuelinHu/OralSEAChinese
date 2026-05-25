from .audio_utils import analyze_wav_features
from .schemas import CorpusType, EvaluateResponse, FeedbackSegment


def expected_duration_ms(corpus_type: CorpusType, hanzi: str, pinyin: str) -> int:
    unit_count = max(len(pinyin.split()), len(hanzi))
    if corpus_type == "pinyin":
        return 1100
    if corpus_type == "word":
        return max(1300, unit_count * 600)
    return max(2200, unit_count * 430)


def evaluate_audio_baseline(
    *,
    audio_content: bytes,
    corpus_type: CorpusType,
    hanzi: str,
    pinyin: str,
) -> EvaluateResponse:
    features = analyze_wav_features(audio_content)
    expected_duration = expected_duration_ms(corpus_type, hanzi, pinyin)
    duration = int(features["duration_ms"])
    duration_ratio = min(duration, expected_duration) / max(duration, expected_duration) if duration and expected_duration else 0
    voiced_ratio = float(features["voiced_ratio"])
    silence_ratio = float(features["silence_ratio"])
    longest_silence_ms = int(features["longest_silence_ms"])
    energy_variation = float(features["energy_variation"])
    rms = float(features["rms"])

    completeness_score = _clamp(100 * duration_ratio * min(1.0, voiced_ratio / 0.55), 35, 100)
    fluency_score = _clamp(100 - abs(1 - duration_ratio) * 38 - silence_ratio * 22 - max(0, longest_silence_ms - 700) / 40, 35, 100)
    accuracy_score = _clamp(completeness_score * 0.72 + min(100, rms * 850) * 0.08 + 18, 35, 100)
    tone_score = _clamp(72 + min(18, energy_variation * 16) - silence_ratio * 12, 35, 96)
    if corpus_type == "sentence":
        fluency_score = _clamp(fluency_score - 3, 35, 100)
    if corpus_type == "pinyin":
        tone_score = _clamp(tone_score + 4, 35, 98)

    overall_score = round(accuracy_score * 0.42 + fluency_score * 0.28 + tone_score * 0.30, 2)
    feedback = _build_feedback(
        duration=duration,
        expected_duration=expected_duration,
        voiced_ratio=voiced_ratio,
        longest_silence_ms=longest_silence_ms,
        energy_variation=energy_variation,
    )

    return EvaluateResponse(
        model_version="baseline-v1",
        overall_score=overall_score,
        accuracy_score=round(accuracy_score, 2),
        fluency_score=round(fluency_score, 2),
        tone_score=round(tone_score, 2),
        feedback=feedback,
    )


def _build_feedback(
    *,
    duration: int,
    expected_duration: int,
    voiced_ratio: float,
    longest_silence_ms: int,
    energy_variation: float,
) -> list[FeedbackSegment]:
    feedback = [
        FeedbackSegment(
            label="模型版本",
            message="baseline-v1 已基于真实 WAV 音频提取时长、能量和停顿特征进行评分。",
        )
    ]
    if duration < expected_duration * 0.65:
        feedback.append(FeedbackSegment(label="完整度", message="录音时长偏短，可能没有完整读完。", severity="warning"))
    elif duration > expected_duration * 1.55:
        feedback.append(FeedbackSegment(label="流利度", message="录音时长偏长，建议减少犹豫和重复。", severity="warning"))
    else:
        feedback.append(FeedbackSegment(label="完整度", message="录音时长与目标语料基本匹配。"))

    if voiced_ratio < 0.45:
        feedback.append(FeedbackSegment(label="有效语音", message="有效语音占比较低，录音中可能有较多静音。", severity="warning"))
    if longest_silence_ms > 900:
        feedback.append(FeedbackSegment(label="停顿", message="检测到较长停顿，建议保持更连续的朗读。", severity="warning"))
    if energy_variation < 0.25:
        feedback.append(FeedbackSegment(label="声调", message="能量变化较小，后续声调模型会进一步判断声调起伏。"))
    return feedback


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))

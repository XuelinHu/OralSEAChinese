import re
from statistics import mean, median

from .alignment import align_syllable_segments
from .audio_utils import analyze_wav_features, estimate_pitch_track, read_wav_signal
from .schemas import AudioFeatureSummary, CorpusType, EvaluateResponse, FeedbackSegment, SyllableAnalysis
from .tone_calibration import adjust_tone_score, classify_tone_from_features


TONE_MARKS = {
    "ā": ("a", 1),
    "á": ("a", 2),
    "ǎ": ("a", 3),
    "à": ("a", 4),
    "ē": ("e", 1),
    "é": ("e", 2),
    "ě": ("e", 3),
    "è": ("e", 4),
    "ī": ("i", 1),
    "í": ("i", 2),
    "ǐ": ("i", 3),
    "ì": ("i", 4),
    "ō": ("o", 1),
    "ó": ("o", 2),
    "ǒ": ("o", 3),
    "ò": ("o", 4),
    "ū": ("u", 1),
    "ú": ("u", 2),
    "ǔ": ("u", 3),
    "ù": ("u", 4),
    "ǖ": ("ü", 1),
    "ǘ": ("ü", 2),
    "ǚ": ("ü", 3),
    "ǜ": ("ü", 4),
    "ń": ("n", 2),
    "ň": ("n", 3),
    "ǹ": ("n", 4),
    "ḿ": ("m", 2),
}

PINYIN_TOKEN_PATTERN = re.compile(r"[A-Za-züÜvV:āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜńňǹḿ]+[1-5]?")
HANZI_PATTERN = re.compile(r"[\u4e00-\u9fff]")
TONE_LABELS = {
    1: "一声",
    2: "二声",
    3: "三声",
    4: "四声",
    5: "轻声",
}


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
    return evaluate_audio_tone_segment(
        audio_content=audio_content,
        corpus_type=corpus_type,
        hanzi=hanzi,
        pinyin=pinyin,
    )


def evaluate_audio_tone_segment(
    *,
    audio_content: bytes,
    corpus_type: CorpusType,
    hanzi: str,
    pinyin: str,
) -> EvaluateResponse:
    features = analyze_wav_features(audio_content)
    signal = read_wav_signal(audio_content)
    pitch_track = estimate_pitch_track(signal["samples"], signal["sample_rate"])
    pitch_values = [float(item["f0_hz"]) for item in pitch_track if float(item["f0_hz"]) > 0]
    pitch_coverage = len(pitch_values) / len(pitch_track) if pitch_track else 0.0
    syllables = _parse_pinyin_syllables(pinyin)
    syllable_analysis = _analyze_syllables(
        syllables=syllables,
        hanzi=hanzi,
        samples=signal["samples"],
        sample_rate=signal["sample_rate"],
        pitch_track=pitch_track,
        duration_ms=int(features["duration_ms"]),
    )

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
    baseline_tone_score = _clamp(72 + min(18, energy_variation * 16) - silence_ratio * 12, 35, 96)
    segment_tone_score = (
        mean(segment.tone_score for segment in syllable_analysis)
        if syllable_analysis
        else baseline_tone_score
    )
    tone_score = _clamp(segment_tone_score * 0.86 + baseline_tone_score * 0.14, 35, 98)
    accuracy_score = _clamp(completeness_score * 0.58 + tone_score * 0.27 + min(100, rms * 850) * 0.05 + 10, 35, 100)
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
        syllable_analysis=syllable_analysis,
    )

    return EvaluateResponse(
        model_version="tone-align-calibrated-v1",
        overall_score=overall_score,
        accuracy_score=round(accuracy_score, 2),
        fluency_score=round(fluency_score, 2),
        tone_score=round(tone_score, 2),
        feedback=feedback,
        audio_features=AudioFeatureSummary(
            duration_ms=duration,
            sample_rate=int(features["sample_rate"]),
            channels=int(features["channels"]),
            voiced_ratio=voiced_ratio,
            silence_ratio=silence_ratio,
            longest_silence_ms=longest_silence_ms,
            pitch_coverage=round(pitch_coverage, 4),
            mean_f0_hz=round(median(pitch_values), 2) if pitch_values else None,
        ),
        syllable_analysis=syllable_analysis,
    )


def _build_feedback(
    *,
    duration: int,
    expected_duration: int,
    voiced_ratio: float,
    longest_silence_ms: int,
    energy_variation: float,
    syllable_analysis: list[SyllableAnalysis],
) -> list[FeedbackSegment]:
    feedback = [
        FeedbackSegment(
            label="模型版本",
            message="tone-align-calibrated-v1 已基于真实 WAV 音频提取时长、能量、停顿和基频走势，并生成音节级对齐与声调分析。",
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
    if syllable_analysis:
        feedback.append(
            FeedbackSegment(
                label="音节声调",
                message=f"已生成 {len(syllable_analysis)} 个音节的时间段和声调走势评分。",
            )
        )
        low_segments = sorted(syllable_analysis, key=lambda item: item.tone_score)[:3]
        for segment in low_segments:
            if segment.tone_score < 72:
                feedback.append(
                    FeedbackSegment(
                        label=f"{segment.hanzi or segment.syllable} 声调",
                        message=segment.message,
                        severity="warning",
                    )
                )
    return feedback


def _parse_pinyin_syllables(pinyin: str) -> list[dict[str, int | str]]:
    syllables: list[dict[str, int | str]] = []
    for raw_token in PINYIN_TOKEN_PATTERN.findall(pinyin):
        normalized = ""
        tone = None
        token = raw_token.strip()
        if token[-1:].isdigit():
            tone = int(token[-1])
            token = token[:-1]
        for char in token:
            lower = char.lower()
            if lower in TONE_MARKS:
                base, marked_tone = TONE_MARKS[lower]
                normalized += base
                tone = marked_tone
            elif lower == "v":
                normalized += "ü"
            else:
                normalized += lower
        normalized = normalized.replace("u:", "ü").strip()
        if normalized:
            syllables.append({"display": raw_token, "normalized": normalized, "tone": tone or 5})
    return syllables


def _analyze_syllables(
    *,
    syllables: list[dict[str, int | str]],
    hanzi: str,
    samples: list[float],
    sample_rate: int,
    pitch_track: list[dict[str, float | int]],
    duration_ms: int,
) -> list[SyllableAnalysis]:
    if not syllables:
        return []

    hanzi_chars = HANZI_PATTERN.findall(hanzi)
    aligned_segments = align_syllable_segments(
        syllable_count=len(syllables),
        samples=samples,
        sample_rate=sample_rate,
        duration_ms=duration_ms,
        pitch_track=pitch_track,
    )
    analysis: list[SyllableAnalysis] = []
    for index, syllable in enumerate(syllables):
        segment = aligned_segments[index]
        start_ms = int(segment["start_ms"])
        end_ms = int(segment["end_ms"])
        segment_frames = [
            item
            for item in pitch_track
            if start_ms <= int(item["time_ms"]) <= end_ms and float(item["f0_hz"]) > 0
        ]
        score, predicted_tone, confidence, message = _score_tone_segment(
            expected_tone=int(syllable["tone"]),
            frames=segment_frames,
        )
        analysis.append(
            SyllableAnalysis(
                syllable=str(syllable["display"]),
                hanzi=hanzi_chars[index] if index < len(hanzi_chars) else None,
                expected_tone=int(syllable["tone"]),
                predicted_tone=predicted_tone,
                start_ms=start_ms,
                end_ms=end_ms,
                tone_score=score,
                confidence=confidence,
                alignment_confidence=float(segment["confidence"]),
                alignment_method=str(segment["method"]),
                message=message,
            )
        )
    return analysis


def _score_tone_segment(
    *,
    expected_tone: int,
    frames: list[dict[str, float | int]],
) -> tuple[float, int | None, float, str]:
    f0_values = [float(item["f0_hz"]) for item in frames if float(item["f0_hz"]) > 0]
    if len(f0_values) < 3:
        message = f"目标为 {TONE_LABELS.get(expected_tone, '未知声调')}，但该音节可用基频不足，建议重新采集更清晰的录音。"
        return 42.0, None, 0.0, message

    third = max(1, len(f0_values) // 3)
    start_f0 = mean(f0_values[:third])
    middle_f0 = mean(f0_values[third : third * 2] or f0_values)
    end_f0 = mean(f0_values[-third:])
    mean_f0 = max(1.0, mean(f0_values))
    slope = (end_f0 - start_f0) / mean_f0
    dip = (min(start_f0, end_f0) - middle_f0) / mean_f0
    variation = (max(f0_values) - min(f0_values)) / mean_f0
    confidence = _clamp(mean(float(item["confidence"]) for item in frames), 0.0, 1.0)
    predicted_tone = classify_tone_from_features(slope=slope, dip=dip, variation=variation)
    score = _score_expected_tone(
        expected_tone=expected_tone,
        predicted_tone=predicted_tone,
        slope=slope,
        dip=dip,
        variation=variation,
        confidence=confidence,
    )
    message = _tone_message(expected_tone=expected_tone, predicted_tone=predicted_tone, score=score)
    calibrated_score = adjust_tone_score(expected_tone=expected_tone, score=score, confidence=confidence)
    return round(_clamp(calibrated_score, 35, 100), 2), predicted_tone, round(confidence, 3), message


def _score_expected_tone(
    *,
    expected_tone: int,
    predicted_tone: int,
    slope: float,
    dip: float,
    variation: float,
    confidence: float,
) -> float:
    if expected_tone == 1:
        score = 94 - abs(slope) * 140 - variation * 35
    elif expected_tone == 2:
        score = 62 + max(0.0, slope) * 210 - max(0.0, -slope) * 95
    elif expected_tone == 3:
        score = 56 + max(0.0, dip) * 260 + max(0.0, variation - 0.08) * 45
    elif expected_tone == 4:
        score = 62 + max(0.0, -slope) * 210 - max(0.0, slope) * 95
    else:
        score = 78 - variation * 24 - abs(slope) * 32

    if predicted_tone == expected_tone:
        score += 8
    score *= 0.72 + confidence * 0.28
    return _clamp(score, 35, 100)


def _tone_message(*, expected_tone: int, predicted_tone: int | None, score: float) -> str:
    expected = TONE_LABELS.get(expected_tone, "未知声调")
    predicted = TONE_LABELS.get(predicted_tone, "无法稳定判断") if predicted_tone is not None else "无法稳定判断"
    if score >= 82:
        return f"目标为 {expected}，检测到的声调走势基本匹配。"
    return f"目标为 {expected}，当前检测更接近 {predicted}；建议对照标准音频加强该音节声调走势。"


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))

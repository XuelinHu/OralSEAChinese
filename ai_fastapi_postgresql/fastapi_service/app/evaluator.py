from .schemas import EvaluateRequest, EvaluateResponse, FeedbackSegment


def _expected_duration_ms(payload: EvaluateRequest) -> int:
    unit_count = max(len(payload.pinyin.split()), len(payload.hanzi))
    if payload.corpus_type == "pinyin":
        return 1200
    if payload.corpus_type == "word":
        return max(1400, unit_count * 650)
    return max(2200, unit_count * 420)


def evaluate_pronunciation(payload: EvaluateRequest) -> EvaluateResponse:
    expected_duration = _expected_duration_ms(payload)
    duration = payload.duration_ms or expected_duration
    duration_ratio = min(duration, expected_duration) / max(duration, expected_duration)

    type_bonus = {
        "pinyin": 2.0,
        "word": 0.0,
        "sentence": -2.0,
    }[payload.corpus_type]

    fluency_score = round(max(60.0, 92.0 * duration_ratio + type_bonus), 2)
    accuracy_score = round(max(60.0, 88.0 + type_bonus), 2)
    tone_score = round(max(60.0, 86.0 + type_bonus), 2)
    overall_score = round(accuracy_score * 0.45 + fluency_score * 0.25 + tone_score * 0.30, 2)

    feedback = [
        FeedbackSegment(label="发音完整度", message="未收到音频文件，已使用文本和时长规则评分。"),
        FeedbackSegment(label="声调", message="建议通过音频上传接口使用 baseline-v1 获取真实音频特征评分。"),
    ]
    if payload.corpus_type == "sentence":
        feedback.append(
            FeedbackSegment(label="句子流利度", message="句子练习会重点关注停顿、连读和整体语调。", severity="warning")
        )

    return EvaluateResponse(
        model_version="duration-rule-v1",
        overall_score=overall_score,
        accuracy_score=accuracy_score,
        fluency_score=fluency_score,
        tone_score=tone_score,
        feedback=feedback,
    )

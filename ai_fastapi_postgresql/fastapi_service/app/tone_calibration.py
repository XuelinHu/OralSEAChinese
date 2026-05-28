import json
import os
from pathlib import Path
from typing import Any


DEFAULT_CALIBRATION: dict[str, Any] = {
    "version": "default",
    "score_bias_by_expected_tone": {},
    "classification_thresholds": {
        "rising_slope": 0.08,
        "falling_slope": -0.08,
        "third_tone_dip": 0.08,
        "third_tone_variation": 0.10,
        "level_abs_slope": 0.07,
        "level_variation": 0.18,
    },
}


_CALIBRATION_CACHE: dict[str, Any] | None = None


def load_tone_calibration() -> dict[str, Any]:
    global _CALIBRATION_CACHE
    if _CALIBRATION_CACHE is not None:
        return _CALIBRATION_CACHE

    path = Path(os.getenv("TONE_CALIBRATION_PATH", _default_calibration_path()))
    if not path.exists():
        _CALIBRATION_CACHE = DEFAULT_CALIBRATION
        return _CALIBRATION_CACHE

    try:
        with path.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
    except (OSError, json.JSONDecodeError):
        _CALIBRATION_CACHE = DEFAULT_CALIBRATION
        return _CALIBRATION_CACHE

    _CALIBRATION_CACHE = {
        **DEFAULT_CALIBRATION,
        **loaded,
        "classification_thresholds": {
            **DEFAULT_CALIBRATION["classification_thresholds"],
            **loaded.get("classification_thresholds", {}),
        },
        "score_bias_by_expected_tone": loaded.get("score_bias_by_expected_tone", {}),
    }
    return _CALIBRATION_CACHE


def reset_tone_calibration_cache() -> None:
    global _CALIBRATION_CACHE
    _CALIBRATION_CACHE = None


def classify_tone_from_features(*, slope: float, dip: float, variation: float) -> int:
    thresholds = load_tone_calibration()["classification_thresholds"]
    if dip > float(thresholds["third_tone_dip"]) and variation > float(thresholds["third_tone_variation"]):
        return 3
    if slope > float(thresholds["rising_slope"]):
        return 2
    if slope < float(thresholds["falling_slope"]):
        return 4
    if abs(slope) <= float(thresholds["level_abs_slope"]) and variation <= float(thresholds["level_variation"]):
        return 1
    return 5


def adjust_tone_score(*, expected_tone: int, score: float, confidence: float) -> float:
    calibration = load_tone_calibration()
    bias = float(calibration["score_bias_by_expected_tone"].get(str(expected_tone), 0.0))
    if confidence < 0.25:
        bias *= 0.5
    return score + bias


def build_calibration_from_error_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    tone_scores: dict[str, list[float]] = {}
    for sample in samples:
        expected_tone = sample.get("expected_tone")
        tone_score = sample.get("tone_score")
        if expected_tone is None or tone_score is None:
            continue
        tone_scores.setdefault(str(expected_tone), []).append(float(tone_score))

    score_bias_by_expected_tone: dict[str, float] = {}
    error_threshold_by_expected_tone: dict[str, float] = {}
    observed_error_score_by_expected_tone: dict[str, dict[str, float | int]] = {}
    for expected_tone, scores in tone_scores.items():
        average_error_score = sum(scores) / len(scores)
        observed_error_score_by_expected_tone[expected_tone] = {
            "count": len(scores),
            "average": round(average_error_score, 2),
            "minimum": round(min(scores), 2),
            "maximum": round(max(scores), 2),
        }
        error_threshold_by_expected_tone[expected_tone] = round(min(78.0, max(55.0, average_error_score + 10.0)), 2)
        if len(scores) < 2 or average_error_score <= 58.0:
            continue
        bias = round(-min(18.0, average_error_score - 58.0), 2)
        if bias:
            score_bias_by_expected_tone[expected_tone] = bias

    return {
        "version": "tone-calibration-v1",
        "sample_count": len(samples),
        "tone_error_sample_count": len(samples),
        "score_bias_by_expected_tone": score_bias_by_expected_tone,
        "error_threshold_by_expected_tone": error_threshold_by_expected_tone,
        "observed_error_score_by_expected_tone": observed_error_score_by_expected_tone,
        "classification_thresholds": DEFAULT_CALIBRATION["classification_thresholds"],
        "notes": "Generated from corpus_annotation rows where error_type='tone'. Current calibration uses negative score bias only when annotated errors score too high.",
    }


def _default_calibration_path() -> str:
    return str(Path(__file__).resolve().parents[1] / "models" / "tone_calibration.json")

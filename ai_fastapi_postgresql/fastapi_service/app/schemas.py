from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


CorpusType = Literal["pinyin", "word", "sentence"]


class EvaluateRequest(BaseModel):
    practice_record_id: UUID | None = None
    corpus_item_id: UUID
    corpus_type: CorpusType
    hanzi: str = Field(min_length=1)
    pinyin: str = Field(min_length=1)
    audio_url: str | None = None
    duration_ms: int | None = Field(default=None, ge=0)


class FeedbackSegment(BaseModel):
    label: str
    message: str
    severity: Literal["info", "warning", "error"] = "info"


class AudioFeatureSummary(BaseModel):
    duration_ms: int
    sample_rate: int
    channels: int
    voiced_ratio: float
    silence_ratio: float
    longest_silence_ms: int
    pitch_coverage: float
    mean_f0_hz: float | None = None


class SyllableAnalysis(BaseModel):
    syllable: str
    hanzi: str | None = None
    expected_tone: int | None = None
    predicted_tone: int | None = None
    start_ms: int
    end_ms: int
    tone_score: float
    confidence: float
    alignment_confidence: float = 0.0
    alignment_method: str = "unknown"
    message: str


class EvaluateResponse(BaseModel):
    model_version: str
    overall_score: float
    accuracy_score: float
    fluency_score: float
    tone_score: float
    feedback: list[FeedbackSegment]
    audio_features: AudioFeatureSummary | None = None
    syllable_analysis: list[SyllableAnalysis] = Field(default_factory=list)


class TrainRequest(BaseModel):
    task_name: str = Field(min_length=1)
    corpus_type: CorpusType | None = None
    min_annotation_count: int = Field(default=0, ge=0)

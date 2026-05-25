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


class EvaluateResponse(BaseModel):
    model_version: str
    overall_score: float
    accuracy_score: float
    fluency_score: float
    tone_score: float
    feedback: list[FeedbackSegment]


class TrainRequest(BaseModel):
    task_name: str = Field(min_length=1)
    corpus_type: CorpusType | None = None
    min_annotation_count: int = Field(default=0, ge=0)

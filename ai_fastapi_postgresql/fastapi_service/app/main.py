from uuid import uuid4

from fastapi import FastAPI, File, UploadFile

from .audio_utils import analyze_wav_duration
from .evaluator import evaluate_pronunciation
from .schemas import EvaluateRequest, EvaluateResponse, TrainRequest

app = FastAPI(title="OralSEAChinese AI Service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-fastapi"}


@app.post("/api/v1/pronunciation/evaluate", response_model=EvaluateResponse)
def evaluate(payload: EvaluateRequest) -> EvaluateResponse:
    return evaluate_pronunciation(payload)


@app.post("/api/v1/audio/analyze")
async def analyze_audio(audio: UploadFile = File(...)) -> dict[str, object]:
    content = await audio.read()
    analysis = analyze_wav_duration(content)
    return {
        "filename": audio.filename,
        "content_type": audio.content_type,
        "size": len(content),
        "analysis": analysis,
    }


@app.get("/api/v1/model/versions")
def model_versions() -> dict[str, list[dict[str, object]]]:
    return {
        "items": [
            {
                "version_code": "mock-v1",
                "model_type": "pronunciation-evaluator",
                "description": "规则占位版发音评分，用于跑通第一阶段业务闭环。",
                "is_active": True,
            }
        ]
    }


@app.post("/api/v1/model/train")
def create_training_task(payload: TrainRequest) -> dict[str, object]:
    return {
        "task_id": str(uuid4()),
        "task_name": payload.task_name,
        "status": "pending",
        "message": "训练任务已创建。第一版仅记录任务，不执行真实训练。",
    }

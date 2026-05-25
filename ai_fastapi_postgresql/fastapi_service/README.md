# FastAPI Service

Python FastAPI AI 服务目录。

## 推荐能力边界

FastAPI 服务只处理 AI 和音频评测相关逻辑，不直接承担 APK 的通用业务接口。

建议接口：

- `POST /api/v1/pronunciation/evaluate`
- `GET /api/v1/pronunciation/tasks/{task_id}`
- `POST /api/v1/model/train`
- `GET /api/v1/model/versions`

## 后续初始化建议

```bash
python -m venv .venv
pip install fastapi uvicorn python-multipart pydantic
```

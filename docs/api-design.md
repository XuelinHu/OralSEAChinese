# 接口设计

## Node.js 业务后端

默认地址：`http://127.0.0.1:3100`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 后端健康检查 |
| POST | `/api/v1/auth/login` | 第一版开发登录 |
| GET | `/api/v1/courses` | 课程列表 |
| GET | `/api/v1/courses/:courseId/lessons` | 课时列表 |
| GET | `/api/v1/corpus?type=sentence` | 语料列表，支持 `pinyin`、`word`、`sentence` |
| POST | `/api/v1/practice/evaluate` | 上传录音并调用 AI 评分 |
| GET | `/api/v1/admin/corpus` | 管理端语料列表 |
| POST | `/api/v1/admin/corpus` | 管理端新增语料 |
| PUT | `/api/v1/admin/corpus/:id` | 管理端编辑语料 |
| DELETE | `/api/v1/admin/corpus/:id` | 管理端删除语料 |
| GET | `/api/v1/admin/courses` | 管理端课程列表 |
| POST | `/api/v1/admin/courses` | 管理端新增课程 |
| PUT | `/api/v1/admin/courses/:id` | 管理端编辑课程 |
| GET | `/api/v1/admin/courses/:courseId/lessons` | 管理端课时列表 |
| POST | `/api/v1/admin/lessons` | 管理端新增课时 |
| PUT | `/api/v1/admin/lessons/:id` | 管理端编辑课时 |
| GET | `/api/v1/admin/practice-scores` | 管理端评分记录列表 |
| GET | `/api/v1/admin/practice-scores/:id` | 管理端评分记录详情 |

`/api/v1/practice/evaluate` 在配置 PostgreSQL 后会保存练习记录和评分结果；无数据库时只返回评分结果和 `persistence.persisted=false`。

## FastAPI AI 服务

默认地址：`http://127.0.0.1:8001`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | AI 服务健康检查 |
| POST | `/api/v1/pronunciation/evaluate` | 发音评测 |
| GET | `/api/v1/model/versions` | 模型版本列表 |
| POST | `/api/v1/model/train` | 创建模型训练任务 |
| POST | `/api/v1/audio/analyze` | 分析上传 WAV 音频的时长、采样率和声道数 |

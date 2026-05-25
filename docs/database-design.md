# 数据库设计

数据库使用 PostgreSQL。第一版表结构位于：

- `ai_fastapi_postgresql/database/001_create_tables.sql`
- `ai_fastapi_postgresql/database/002_create_indexes.sql`
- `ai_fastapi_postgresql/database/005_seed_data.sql`

## 核心表

- `app_user`：学习者、教师、管理员、研究人员。
- `course`：课程。
- `lesson`：课时。
- `corpus_item`：语料，支持 `pinyin`、`word`、`sentence`。
- `audio_asset`：标准音频和学习者录音。
- `practice_record`：练习记录。
- `pronunciation_score`：发音评分。
- `corpus_annotation`：人工标注。
- `model_version`：模型版本。
- `model_training_task`：模型训练任务。

## 第一版种子语料

种子数据已经包含拼音、词语和句子：

- 拼音：`妈`、`马`
- 词语：`你好`、`谢谢`
- 句子：`我想学习中文。`、`今天的天气很好。`

## 后端数据访问策略

Node 后端优先使用 `DATABASE_URL` 连接 PostgreSQL。未配置数据库时，会降级使用 `backend_node/src/data/corpus.json`，用于无数据库环境下的冒烟测试。

当 PostgreSQL 可用时：

- 课程接口读取 `course` 和 `lesson`。
- 语料接口读取 `corpus_item`。
- 练习提交会写入 `audio_asset`、`practice_record` 和 `pronunciation_score`。

## 人工标注

`corpus_annotation` 用于沉淀后续模型训练数据。第一版支持：

- 声母错误：`initial`
- 韵母错误：`final`
- 声调错误：`tone`
- 流利度问题：`fluency`
- 整体发音问题：`pronunciation`
- 其他问题：`other`

标注可关联练习记录，并记录起止毫秒和教师/研究人员备注。

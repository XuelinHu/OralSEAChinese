# Database PostgreSQL

PostgreSQL 数据库脚本目录。

## 建议脚本拆分

```text
database/
├── 001_create_tables.sql
├── 002_create_indexes.sql
├── 003_create_views.sql
├── 004_create_functions.sql
└── 005_seed_data.sql
```

## 第一版核心表

- `app_user`
- `course`
- `lesson`
- `corpus_item`
- `standard_audio`
- `practice_record`
- `learner_audio`
- `pronunciation_score`
- `corpus_annotation`
- `model_version`
- `model_training_task`

## 安全要求

不要把数据库账号密码写入 SQL 文件或 README。连接信息放在本地 `.env` 或部署环境变量中。

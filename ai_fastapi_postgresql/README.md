# AI FastAPI PostgreSQL

AI 发音评测服务和数据库脚本目录。

## 目录说明

```text
ai_fastapi_postgresql/
├── fastapi_service/  # Python FastAPI 服务
└── database/         # PostgreSQL 脚本
```

## AI 服务职责

- 接收业务后端传来的录音文件或音频地址
- 执行语音识别、音素对齐、声调分析或模型推理
- 返回发音评分、错误位置和反馈建议
- 管理模型版本、训练任务和评测任务

## 数据库职责

- 用户、课程、语料、音频、练习记录表结构
- 发音评分结果表结构
- 人工标注数据表结构
- 模型训练任务和模型版本表结构
- PostgreSQL 函数、视图、索引和初始化数据

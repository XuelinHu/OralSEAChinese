# OralSEAChinese

<p align="center">
  <img height="20" src="https://img.shields.io/badge/flutter-configured-02569B?logo=flutter&amp;logoColor=white" />
  <img height="20" src="https://img.shields.io/badge/react-19.2.3-61DAFB?logo=react&amp;logoColor=black" />
  <img height="20" src="https://img.shields.io/badge/vite-7.2.7-646CFF?logo=vite&amp;logoColor=white" />
  <img height="20" src="https://img.shields.io/badge/express-5.1.0-000000?logo=express&amp;logoColor=white" />
  <img height="20" src="https://img.shields.io/badge/fastapi-0.121.3-009688?logo=fastapi&amp;logoColor=white" />
  <img height="20" src="https://img.shields.io/badge/postgresql-used-4169E1?logo=postgresql&amp;logoColor=white" />
  <img height="20" src="https://img.shields.io/badge/docker_compose-configured-2496ED?logo=docker&amp;logoColor=white" />
</p>

面向马来西亚学习者的中文发音学习系统。

## 工程结构

```text
OralSEAChinese/
├── apk_flutter/          # Android APK，建议使用 Flutter/Dart 开发
├── admin_web/            # 语料管理后台，React + Vite
├── backend_node/         # 业务后端，Node.js 技术栈
├── ai_fastapi_postgresql/ # AI 发音评测服务、FastAPI、PostgreSQL 数据库脚本
│   ├── fastapi_service/  # Python FastAPI 服务
│   └── database/         # PostgreSQL 表结构、函数、初始化脚本
└── docs/                 # 需求、接口、数据库、部署等文档
```

## 技术路线

- APK：Flutter + Dart，面向 Android 打包 APK。
- 业务后端：Node.js，负责用户、课程、语料、练习记录、文件上传等业务接口。
- 管理后台：React + Vite，负责课程语料和评分记录管理。
- AI 服务：Python FastAPI，负责音频评测、模型调用、训练任务接口。
- 数据库：PostgreSQL，保存用户、课程、语料、练习记录、标注和模型结果。

## 配置安全

数据库账号、密码、服务地址等敏感信息不要提交到代码仓库。后续统一使用 `.env` 或服务器环境变量管理。

## 本地 PostgreSQL

项目提供 `docker-compose.yml`，可启动本地 PostgreSQL：

```bash
docker compose up -d postgres
cd backend_node
cp .env.example .env
npm run db:init
```

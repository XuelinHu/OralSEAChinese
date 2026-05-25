# Backend Node

业务后端目录，使用 Node.js 技术栈。

## 主要职责

- 用户认证与权限
- APK 业务接口
- 课程与语料接口
- 音频上传与文件元数据管理
- 调用 FastAPI AI 发音评测服务
- 管理后台接口
- 与 PostgreSQL 数据库交互

## 推荐技术栈

- Node.js
- NestJS 或 Express
- TypeScript
- PostgreSQL 驱动
- JWT 认证

## 后续初始化建议

如果采用 NestJS：

```bash
npx @nestjs/cli new .
```

如果采用 Express：

```bash
npm init -y
npm install express pg dotenv jsonwebtoken multer
```

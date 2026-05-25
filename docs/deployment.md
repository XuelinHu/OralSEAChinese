# 本地运行说明

## FastAPI AI 服务

```bash
cd ai_fastapi_postgresql/fastapi_service
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

## Node.js 业务后端

```bash
cd backend_node
npm install
PORT=3100 npm run start
```

## 管理后台

```bash
cd admin_web
npm install
npm run dev
```

默认访问地址：

```text
http://127.0.0.1:5173
```

默认连接 Node 后端：

```text
http://127.0.0.1:3100
```

## PostgreSQL 初始化

本项目已提供本地 PostgreSQL：

```bash
docker compose up -d postgres
```

推荐通过 Node 初始化脚本执行所有数据库脚本：

```bash
cd backend_node
cp .env.example .env
# 修改 .env 中的 DATABASE_URL
npm run db:init
```

也可以手动执行 SQL：

```bash
psql "$DATABASE_URL" -f ai_fastapi_postgresql/database/001_create_tables.sql
psql "$DATABASE_URL" -f ai_fastapi_postgresql/database/002_create_indexes.sql
psql "$DATABASE_URL" -f ai_fastapi_postgresql/database/005_seed_data.sql
```

没有配置 `DATABASE_URL` 时，Node 后端会自动使用内置 JSON 种子数据，便于本地先跑通 APK 到 AI 评分的主流程。

## Flutter APK

当前机器的 Flutter 安装路径为 `/home/xuelin/development/flutter/bin/flutter`。如果 shell 中不能直接执行 `flutter`，先配置 PATH：

```bash
export PATH=/home/xuelin/development/flutter/bin:$PATH
```

执行 APK 依赖检查和构建：

```bash
cd apk_flutter
flutter pub get
flutter analyze
flutter test
JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 flutter build apk --debug
```

Android 模拟器访问本机 Node 后端时，APK 默认使用 `http://10.0.2.2:3100`。

APK 已接入真实录音，Android 侧需要麦克风权限。Debug APK 构建命令：

如果本机全局 Gradle 初始化文件注入了仓库配置，导致 Android 构建出现 repository mode 冲突，可使用临时 Gradle 目录隔离：

```bash
JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
GRADLE_USER_HOME=/tmp/oralsea-gradle \
flutter build apk --debug
```

已检测到的 Android 模拟器：

```text
flutter_api36
```

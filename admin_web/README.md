# Admin Web

语料管理后台，使用 React + Vite。

## 功能

- 查看拼音、词语、句子语料
- 按类型筛选语料
- 新增语料
- 编辑语料
- 删除语料
- 查看最近评分记录

## 本地运行

```bash
cd admin_web
npm install
npm run dev
```

默认连接 Node 后端：

```text
http://127.0.0.1:3100
```

如需修改：

```bash
VITE_API_BASE_URL=http://127.0.0.1:3100 npm run dev
```

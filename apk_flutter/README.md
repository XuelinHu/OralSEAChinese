# APK Flutter

Android APK 客户端目录，建议使用 Flutter / Dart 开发。

## 主要功能

- 用户登录与注册
- 中文拼音、声母、韵母、声调学习
- 标准音频播放
- 跟读录音
- 录音上传
- 发音评分结果展示
- 学习进度与历史记录

## 后续初始化建议

在本目录下执行 Flutter 工程初始化：

```bash
flutter create .
```

初始化后建议按功能拆分：

```text
lib/
├── app/
├── features/
│   ├── auth/
│   ├── course/
│   ├── practice/
│   └── profile/
├── shared/
└── main.dart
```

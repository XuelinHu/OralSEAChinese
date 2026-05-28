# AI 发音评测设计

## 第一版策略

第一版已经从 `mock-v1`、`baseline-v1`、`tone-segment-v1` 升级为 `tone-align-calibrated-v1` 本地声调分析原型模型。

`tone-align-calibrated-v1` 不依赖云服务，直接读取 APK 上传的 WAV 音频，提取基础声学特征和基频走势，并结合目标拼音解析声调。它会用有效语音区间和能量谷值估算音节边界，输出整段评分和音节级声调分析；如果存在 `models/tone_calibration.json`，还会加载人工标注生成的校准参数。

## 评分字段

- `overall_score`：总分。
- `accuracy_score`：准确度。
- `fluency_score`：流利度。
- `tone_score`：声调分。
- `feedback`：反馈说明。
- `audio_features`：音频特征摘要，包括时长、采样率、有效语音占比、静音占比、最长停顿、基频覆盖率等。
- `syllable_analysis`：音节级分析，包括目标音节、汉字、期望声调、预测声调、起止时间、声调分、声调置信度、对齐置信度和对齐方法。

## tone-align-calibrated-v1 特征

- 音频时长
- 采样率
- 声道数
- RMS 能量
- 峰值能量
- 有效语音占比
- 静音占比
- 最长停顿时长
- 能量变化程度
- 基频 F0 轨迹
- 拼音声调解析
- 基于能量谷值的轻量音节对齐
- 音节级声调走势评分
- 人工标注驱动的声调分校准

## tone-align-calibrated-v1 评分逻辑

- 完整度：根据目标语料预期朗读时长和有效语音占比估算。
- 流利度：根据时长偏差、静音比例和最长停顿扣分。
- 准确度：当前综合完整度、录音有效性和音节级声调分近似估算。
- 音节对齐：先定位有效语音区间，再在每个预期音节边界附近寻找能量谷值作为边界。
- 声调分：根据拼音声调、对齐后音节内的基频走势和整段能量变化综合估算。
- 校准：`scripts/calibrate_tone_model.py` 会读取 `corpus_annotation` 中的声调错误标注，提取被标注时间段覆盖的音节样本，并生成 `models/tone_calibration.json`。

注意：`tone-align-calibrated-v1` 仍不是最终中文发音评测模型。它已经能输出音节级声调分析，并比平均切分更接近真实发音边界，但当前对齐仍是轻量能量谷值对齐，不是 ASR 或 forced alignment；它也不能精确判断声母、韵母是否正确。它是后续 ASR、音素对齐和训练式声调识别模型接入前的本地原型。

## 后续模型方向

- 接入 ASR，判断朗读文本是否完整。
- 引入 ASR 或 forced alignment，替换当前轻量能量谷值对齐。
- 用真实标注数据训练声调识别模型，重点评估马来西亚学习者常见声调问题。
- 积累人工标注数据后训练发音评分模型。

## 训练数据要求

后续训练真实发音模型至少需要：

- 学习者录音文件
- 目标汉字和拼音
- 人工标注错误类型
- 错误起止时间
- 教师或研究人员备注
- 当前模型评分结果

这些数据已经通过 `audio_asset`、`practice_record`、`pronunciation_score` 和 `corpus_annotation` 开始沉淀。

import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:record/record.dart';

import '../models/corpus_item.dart';
import '../models/pronunciation_score.dart';
import '../services/api_client.dart';

class PracticeScreen extends StatefulWidget {
  const PracticeScreen({super.key, required this.item});

  final CorpusItem item;

  @override
  State<PracticeScreen> createState() => _PracticeScreenState();
}

class _PracticeScreenState extends State<PracticeScreen> {
  final ApiClient _apiClient = ApiClient();
  final AudioRecorder _recorder = AudioRecorder();
  bool _submitting = false;
  bool _recording = false;
  PronunciationScore? _score;
  String? _lastAudioPath;
  DateTime? _recordingStartedAt;

  Future<void> _startRecording() async {
    final permission = await Permission.microphone.request();
    if (!permission.isGranted || !await _recorder.hasPermission()) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('需要麦克风权限才能录音')));
      return;
    }

    final directory = await getTemporaryDirectory();
    final path = '${directory.path}/practice_${DateTime.now().millisecondsSinceEpoch}.wav';
    await _recorder.start(
      const RecordConfig(encoder: AudioEncoder.wav, sampleRate: 16000, numChannels: 1),
      path: path,
    );
    setState(() {
      _recording = true;
      _recordingStartedAt = DateTime.now();
      _lastAudioPath = null;
      _score = null;
    });
  }

  Future<void> _stopAndSubmitPractice() async {
    setState(() {
      _submitting = true;
      _score = null;
    });

    try {
      final audioPath = await _recorder.stop();
      final startedAt = _recordingStartedAt;
      final durationMs = startedAt == null ? null : DateTime.now().difference(startedAt).inMilliseconds;
      if (audioPath == null) {
        throw Exception('录音文件生成失败');
      }
      final score = await _apiClient.submitPractice(widget.item, audioPath: audioPath, durationMs: durationMs);
      if (!mounted) return;
      setState(() {
        _score = score;
        _lastAudioPath = audioPath;
      });
    } finally {
      if (mounted) {
        setState(() {
          _recording = false;
          _submitting = false;
          _recordingStartedAt = null;
        });
      }
    }
  }

  @override
  void dispose() {
    _recorder.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final item = widget.item;
    return Scaffold(
      appBar: AppBar(title: const Text('跟读练习')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(item.hanzi, style: Theme.of(context).textTheme.displaySmall),
            const SizedBox(height: 8),
            Text(item.pinyin, style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(item.translationEn),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: _submitting ? null : (_recording ? _stopAndSubmitPractice : _startRecording),
              icon: Icon(_recording ? Icons.stop : Icons.mic),
              label: Text(_submitting ? '评分中' : (_recording ? '停止录音并评分' : '开始录音')),
            ),
            if (_lastAudioPath != null) ...[
              const SizedBox(height: 12),
              Text('已上传录音：$_lastAudioPath', style: Theme.of(context).textTheme.bodySmall),
            ],
            if (_score != null) ...[
              const SizedBox(height: 24),
              _ScoreTile(label: '总分', value: _score!.overallScore),
              _ScoreTile(label: '准确度', value: _score!.accuracyScore),
              _ScoreTile(label: '流利度', value: _score!.fluencyScore),
              _ScoreTile(label: '声调', value: _score!.toneScore),
            ],
          ],
        ),
      ),
    );
  }
}

class _ScoreTile extends StatelessWidget {
  const _ScoreTile({required this.label, required this.value});

  final String label;
  final double value;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      title: Text(label),
      trailing: Text(value.toStringAsFixed(1)),
    );
  }
}

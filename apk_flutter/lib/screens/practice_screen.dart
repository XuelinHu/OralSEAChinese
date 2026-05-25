import 'package:flutter/material.dart';

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
  bool _submitting = false;
  PronunciationScore? _score;

  Future<void> _submitPractice() async {
    setState(() {
      _submitting = true;
      _score = null;
    });

    try {
      final score = await _apiClient.submitPractice(widget.item);
      if (!mounted) return;
      setState(() => _score = score);
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
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
              onPressed: _submitting ? null : _submitPractice,
              icon: const Icon(Icons.mic),
              label: Text(_submitting ? '评分中' : '模拟录音并评分'),
            ),
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

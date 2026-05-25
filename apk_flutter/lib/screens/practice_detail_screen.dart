import 'package:flutter/material.dart';

import '../models/practice_history.dart';
import '../services/api_client.dart';

class PracticeDetailScreen extends StatefulWidget {
  const PracticeDetailScreen({super.key, required this.practiceRecordId});

  final String practiceRecordId;

  @override
  State<PracticeDetailScreen> createState() => _PracticeDetailScreenState();
}

class _PracticeDetailScreenState extends State<PracticeDetailScreen> {
  final ApiClient _apiClient = ApiClient();
  late Future<PracticeDetail> _future;

  @override
  void initState() {
    super.initState();
    _future = _apiClient.fetchPracticeDetail(widget.practiceRecordId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('练习详情')),
      body: FutureBuilder<PracticeDetail>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('加载失败：${snapshot.error}'));
          }
          final detail = snapshot.data!;
          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Text(detail.hanzi, style: Theme.of(context).textTheme.displaySmall),
              const SizedBox(height: 8),
              Text(detail.pinyin, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 20),
              _ScoreRow(label: '总分', value: detail.overallScore),
              _ScoreRow(label: '准确度', value: detail.accuracyScore),
              _ScoreRow(label: '流利度', value: detail.fluencyScore),
              _ScoreRow(label: '声调', value: detail.toneScore),
              const SizedBox(height: 20),
              if (detail.audioUrl != null)
                Text('录音地址：${_apiClient.resolveMediaUrl(detail.audioUrl!)}')
              else
                const Text('暂无录音文件'),
              const SizedBox(height: 20),
              Text('反馈', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              if (detail.feedback.isEmpty)
                const Text('暂无反馈')
              else
                ...detail.feedback.map((message) => ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: const Icon(Icons.tips_and_updates_outlined),
                      title: Text(message),
                    )),
            ],
          );
        },
      ),
    );
  }
}

class _ScoreRow extends StatelessWidget {
  const _ScoreRow({required this.label, required this.value});

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

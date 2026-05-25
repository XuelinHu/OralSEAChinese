import 'package:flutter/material.dart';

import '../models/practice_history.dart';
import '../services/api_client.dart';
import 'practice_detail_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final ApiClient _apiClient = ApiClient();
  late Future<List<PracticeHistoryItem>> _future;

  @override
  void initState() {
    super.initState();
    _future = _apiClient.fetchPracticeHistory();
  }

  void _reload() {
    setState(() {
      _future = _apiClient.fetchPracticeHistory();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('练习历史'),
        actions: [
          IconButton(onPressed: _reload, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: FutureBuilder<List<PracticeHistoryItem>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('加载失败：${snapshot.error}'));
          }
          final items = snapshot.data ?? [];
          if (items.isEmpty) {
            return const Center(child: Text('暂无练习记录'));
          }
          return ListView.separated(
            itemCount: items.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final item = items[index];
              return ListTile(
                title: Text(item.hanzi),
                subtitle: Text('${item.pinyin} · ${_typeLabel(item.type)} · ${_formatTime(item.createdAt)}'),
                leading: CircleAvatar(child: Text(item.overallScore.toStringAsFixed(0))),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => PracticeDetailScreen(practiceRecordId: item.practiceRecordId),
                    ),
                  );
                },
              );
            },
          );
        },
      ),
    );
  }
}

String _typeLabel(String type) {
  return {
        'pinyin': '拼音',
        'word': '词语',
        'sentence': '句子',
      }[type] ??
      type;
}

String _formatTime(DateTime time) {
  final local = time.toLocal();
  return '${local.year}-${local.month.toString().padLeft(2, '0')}-${local.day.toString().padLeft(2, '0')} '
      '${local.hour.toString().padLeft(2, '0')}:${local.minute.toString().padLeft(2, '0')}';
}

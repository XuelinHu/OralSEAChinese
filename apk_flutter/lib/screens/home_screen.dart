import 'package:flutter/material.dart';

import '../models/corpus_item.dart';
import '../services/api_client.dart';
import 'history_screen.dart';
import 'practice_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiClient _apiClient = ApiClient();
  String _selectedType = 'sentence';
  late Future<List<CorpusItem>> _future;

  @override
  void initState() {
    super.initState();
    _future = _apiClient.fetchCorpus(type: _selectedType);
  }

  void _changeType(String type) {
    setState(() {
      _selectedType = type;
      _future = _apiClient.fetchCorpus(type: type);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('中文发音练习'),
        actions: [
          IconButton(
            tooltip: '练习历史',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const HistoryScreen()),
              );
            },
            icon: const Icon(Icons.history),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'pinyin', label: Text('拼音')),
                ButtonSegment(value: 'word', label: Text('词语')),
                ButtonSegment(value: 'sentence', label: Text('句子')),
              ],
              selected: {_selectedType},
              onSelectionChanged: (values) => _changeType(values.first),
            ),
          ),
          Expanded(
            child: FutureBuilder<List<CorpusItem>>(
              future: _future,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  return Center(child: Text('加载失败：${snapshot.error}'));
                }
                final items = snapshot.data ?? [];
                return ListView.separated(
                  itemCount: items.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final item = items[index];
                    return ListTile(
                      title: Text(item.hanzi),
                      subtitle: Text(item.pinyin),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(builder: (_) => PracticeScreen(item: item)),
                        );
                      },
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/corpus_item.dart';
import '../models/pronunciation_score.dart';

class ApiClient {
  ApiClient({this.baseUrl = 'http://10.0.2.2:3100'});

  final String baseUrl;

  Future<List<CorpusItem>> fetchCorpus({String? type}) async {
    final query = type == null ? '' : '?type=$type';
    final response = await http.get(Uri.parse('$baseUrl/api/v1/corpus$query'));
    if (response.statusCode != 200) {
      throw Exception('Failed to load corpus: ${response.statusCode}');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final items = data['items'] as List<dynamic>;
    return items.map((item) => CorpusItem.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<PronunciationScore> submitPractice(CorpusItem item) async {
    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/v1/practice/evaluate'));
    request.fields['corpusItemId'] = item.id;
    request.fields['durationMs'] = item.type == 'sentence' ? '2800' : '1600';
    request.files.add(http.MultipartFile.fromString('audio', 'placeholder-audio', filename: 'practice.wav'));

    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode != 200) {
      throw Exception('Failed to evaluate: ${response.statusCode}');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return PronunciationScore.fromJson(data['score'] as Map<String, dynamic>);
  }
}

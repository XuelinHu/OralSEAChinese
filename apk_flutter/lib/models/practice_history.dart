class PracticeHistoryItem {
  const PracticeHistoryItem({
    required this.practiceRecordId,
    required this.createdAt,
    required this.audioUrl,
    required this.hanzi,
    required this.pinyin,
    required this.type,
    required this.overallScore,
    required this.accuracyScore,
    required this.fluencyScore,
    required this.toneScore,
  });

  final String practiceRecordId;
  final DateTime createdAt;
  final String? audioUrl;
  final String hanzi;
  final String pinyin;
  final String type;
  final double overallScore;
  final double accuracyScore;
  final double fluencyScore;
  final double toneScore;

  factory PracticeHistoryItem.fromJson(Map<String, dynamic> json) {
    final corpusItem = json['corpusItem'] as Map<String, dynamic>;
    final score = json['score'] as Map<String, dynamic>;
    return PracticeHistoryItem(
      practiceRecordId: json['practiceRecordId'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      audioUrl: json['audioUrl'] as String?,
      hanzi: corpusItem['hanzi'] as String,
      pinyin: corpusItem['pinyin'] as String,
      type: corpusItem['type'] as String,
      overallScore: (score['overallScore'] as num).toDouble(),
      accuracyScore: (score['accuracyScore'] as num).toDouble(),
      fluencyScore: (score['fluencyScore'] as num).toDouble(),
      toneScore: (score['toneScore'] as num).toDouble(),
    );
  }
}

class PracticeDetail {
  const PracticeDetail({
    required this.practiceRecordId,
    required this.createdAt,
    required this.audioUrl,
    required this.hanzi,
    required this.pinyin,
    required this.type,
    required this.overallScore,
    required this.accuracyScore,
    required this.fluencyScore,
    required this.toneScore,
    required this.feedback,
  });

  final String practiceRecordId;
  final DateTime createdAt;
  final String? audioUrl;
  final String hanzi;
  final String pinyin;
  final String type;
  final double overallScore;
  final double accuracyScore;
  final double fluencyScore;
  final double toneScore;
  final List<String> feedback;

  factory PracticeDetail.fromJson(Map<String, dynamic> json) {
    final corpusItem = json['corpusItem'] as Map<String, dynamic>;
    final score = json['score'] as Map<String, dynamic>;
    final audio = json['audio'] as Map<String, dynamic>?;
    final rawFeedback = score['feedback'];
    return PracticeDetail(
      practiceRecordId: json['practiceRecordId'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      audioUrl: audio?['storagePath'] as String?,
      hanzi: corpusItem['hanzi'] as String,
      pinyin: corpusItem['pinyin'] as String,
      type: corpusItem['type'] as String,
      overallScore: (score['overallScore'] as num).toDouble(),
      accuracyScore: (score['accuracyScore'] as num).toDouble(),
      fluencyScore: (score['fluencyScore'] as num).toDouble(),
      toneScore: (score['toneScore'] as num).toDouble(),
      feedback: rawFeedback is List
          ? rawFeedback
              .map((item) => item is Map<String, dynamic> ? item['message']?.toString() ?? '' : item.toString())
              .where((item) => item.isNotEmpty)
              .toList()
          : const [],
    );
  }
}

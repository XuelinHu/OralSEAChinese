class CorpusItem {
  const CorpusItem({
    required this.id,
    required this.type,
    required this.hanzi,
    required this.pinyin,
    required this.translationEn,
    required this.difficulty,
  });

  final String id;
  final String type;
  final String hanzi;
  final String pinyin;
  final String translationEn;
  final int difficulty;

  factory CorpusItem.fromJson(Map<String, dynamic> json) {
    return CorpusItem(
      id: json['id'] as String,
      type: json['type'] as String,
      hanzi: json['hanzi'] as String,
      pinyin: json['pinyin'] as String,
      translationEn: json['translationEn'] as String? ?? '',
      difficulty: json['difficulty'] as int? ?? 1,
    );
  }
}

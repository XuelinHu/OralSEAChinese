class PronunciationScore {
  const PronunciationScore({
    required this.overallScore,
    required this.accuracyScore,
    required this.fluencyScore,
    required this.toneScore,
  });

  final double overallScore;
  final double accuracyScore;
  final double fluencyScore;
  final double toneScore;

  factory PronunciationScore.fromJson(Map<String, dynamic> json) {
    return PronunciationScore(
      overallScore: (json['overall_score'] as num).toDouble(),
      accuracyScore: (json['accuracy_score'] as num).toDouble(),
      fluencyScore: (json['fluency_score'] as num).toDouble(),
      toneScore: (json['tone_score'] as num).toDouble(),
    );
  }
}

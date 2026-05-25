import 'package:flutter_test/flutter_test.dart';

import 'package:oralsea_chinese_apk/main.dart';

void main() {
  testWidgets('App renders practice home screen', (WidgetTester tester) async {
    await tester.pumpWidget(const OralSeaChineseApp());

    expect(find.text('中文发音练习'), findsOneWidget);
    expect(find.text('拼音'), findsOneWidget);
    expect(find.text('词语'), findsOneWidget);
    expect(find.text('句子'), findsOneWidget);
  });
}

import 'package:flutter/material.dart';

import 'screens/home_screen.dart';

void main() {
  runApp(const OralSeaChineseApp());
}

class OralSeaChineseApp extends StatelessWidget {
  const OralSeaChineseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OralSEA Chinese',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

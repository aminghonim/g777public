import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return const Scaffold(
      backgroundColor: Colors.transparent,
      body: Center(
        child: Text(
          'SETTINGS PORTAL',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, fontFamily: 'Oxanium'),
        ),
      ),
    );
  }
}

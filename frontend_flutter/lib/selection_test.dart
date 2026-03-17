import 'package:flutter/material.dart';

/// Minimal test to verify SelectionArea works on this Linux build.
/// Run: flutter run -d linux -t lib/selection_test.dart
void main() {
  runApp(
    MaterialApp(
      home: Scaffold(
        body: Center(
          child: SelectionArea(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  'TRY SELECT THIS TEXT WITH MOUSE',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 20),
                Container(
                  padding: const EdgeInsets.all(16),
                  color: Colors.grey.shade200,
                  child: const Text(
                    'Error: Connection refused at 127.0.0.1:8080\nTry copying this text',
                    style: TextStyle(fontSize: 16, color: Colors.red),
                  ),
                ),
                const SizedBox(height: 20),
                const SelectableText(
                  'THIS IS SelectableText - should ALWAYS be copyable',
                  style: TextStyle(fontSize: 18, color: Colors.blue),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
}

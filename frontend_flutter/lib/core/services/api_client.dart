import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

/// Global API Client Provider
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

/// G777 API Client
/// Handles standard HTTP requests and SSE streams.
class ApiClient {
  final String baseUrl = 'http://localhost:8001'; // Default dev backend

  Future<Map<String, dynamic>> get(String path) async {
    final response = await http.get(Uri.parse('$baseUrl$path'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Failed to load data: ${response.statusCode}');
  }

  /// Minimal SSE Implementation for real-time streams
  Stream<Map<String, dynamic>> streamGet(String path) async* {
    // In production, this would use a persistent HTTP connection (EventSource)
    // For now, we provide a mock stream that yields empty pulses to prevent UI blocking
    while (true) {
      await Future.delayed(const Duration(seconds: 10));
      yield {'type': 'HEARTBEAT', 'data': {}};
    }
  }
}

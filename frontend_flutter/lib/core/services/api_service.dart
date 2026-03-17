import 'dart:convert';
import 'dart:developer' as dev;
import 'package:http/http.dart' as http;
import 'package:g777_client/core/network/port_discovery.dart';

/// G777 API Service - Hardened Singleton (Clean Core Edition)
/// Handles dynamic port discovery and secure handshake
class ApiService {
  // Instance state
  int? _port;
  String? _token;
  bool _initialized = false;

  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  /// Initialize Discovery
  Future<void> init() async {
    if (_initialized && _port != null) return;

    // Retry up to 3 times to handle backend restarts
    for (int i = 0; i < 3; i++) {
      final session = await PortDiscovery.getActiveSession();
      if (session != null) {
        _port = session['port'];
        _token = session['token'];
        _initialized = true;
        dev.log('[API] Session initialized on port $_port', name: 'G777.API');
        return;
      }
      await Future.delayed(const Duration(milliseconds: 500));
    }
    dev.log(
      '[API] Failed to discover active session after retries',
      name: 'G777.API',
    );
    _initialized = true;
  }

  String get baseUrl => 'http://127.0.0.1:${_port ?? 8000}';

  Map<String, String> get _headers {
    final headers = {'Content-Type': 'application/json'};
    if (_token != null) {
      headers['Authorization'] = 'Bearer $_token';
      headers['X-G777-Auth-Token'] = _token!;
    }
    return headers;
  }

  /// Health Check
  Future<Map<String, dynamic>> checkHealth() async {
    await init();
    final response = await http.get(
      Uri.parse('$baseUrl/health'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Health check failed: ${response.statusCode}');
  }

  // --- MARKET INTELLIGENCE (Opportunity Hunter) ---

  /// Opportunity Hunter - Trigger
  Future<Map<String, dynamic>> triggerScan({
    required String type,
    required String keyword,
    int scrollingDepth = 2,
  }) async {
    await init();
    final uri = Uri.parse('$baseUrl/intelligence/trigger_scan').replace(
      queryParameters: {
        'scan_type': type,
        'keyword': keyword,
        'scrolling_depth': scrollingDepth.toString(),
      },
    );
    final response = await http.post(uri, headers: _headers);
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Trigger scan failed: ${response.statusCode}');
  }

  /// Opportunity Hunter - Fetch
  Future<Map<String, dynamic>> getOpportunities({
    int limit = 20,
    String source = 'social',
  }) async {
    await init();
    final uri = Uri.parse(
      '$baseUrl/intelligence/opportunities',
    ).replace(queryParameters: {'limit': limit.toString(), 'source': source});
    final response = await http.get(uri, headers: _headers);
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Get opportunities failed: ${response.statusCode}');
  }
}

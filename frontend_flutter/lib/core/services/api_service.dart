import 'dart:convert';
import 'dart:developer' as dev;
import 'package:http/http.dart' as http;
import 'package:g777_client/core/network/port_discovery.dart';

/// G777 API Service - Hardened Singleton
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

  String get baseUrl => 'http://127.0.0.1:${_port ?? 8081}';

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

  /// Group Sender - Upload Excel (Unified Endpoint)
  Future<Map<String, dynamic>> uploadExcel(String filePath) async {
    await init();
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/group_sender/upload'),
    );
    request.headers.addAll(_headers);
    request.files.add(await http.MultipartFile.fromPath('file', filePath));

    var response = await request.send();
    var responseBody = await response.stream.bytesToString();

    if (response.statusCode == 200) {
      return json.decode(responseBody);
    }
    throw Exception('Upload failed: ${response.statusCode}');
  }

  /// Group Sender - Launch Campaign
  Future<Map<String, dynamic>> launchCampaign({
    required List<String> messages,
    required String sheetName,
    int delayMin = 5,
    int delayMax = 15,
    String? mediaPath,
    String? groupLink,
  }) async {
    await init();
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/group_sender/launch'),
    );
    request.headers.addAll(_headers);

    // Send messages as JSON string for reliability
    request.fields['messages'] = json.encode(
      messages.where((m) => m.trim().isNotEmpty).toList(),
    );

    request.fields['sheet_name'] = sheetName;
    request.fields['delay_min'] = delayMin.toString();
    request.fields['delay_max'] = delayMax.toString();

    if (groupLink != null && groupLink.trim().isNotEmpty) {
      request.fields['group_link'] = groupLink;
    }

    if (mediaPath != null) {
      request.files.add(
        await http.MultipartFile.fromPath('media_file', mediaPath),
      );
    }

    var response = await request.send();
    var responseBody = await response.stream.bytesToString();

    if (response.statusCode == 200) {
      return json.decode(responseBody);
    }
    throw Exception('Launch failed: ${response.statusCode}');
  }

  /// Group Sender - Preview Contacts from a specific sheet
  Future<Map<String, dynamic>> getContacts(String sheetName) async {
    await init();
    final response = await http.get(
      Uri.parse('$baseUrl/api/group_sender/preview?sheet_name=$sheetName'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Preview failed: ${response.statusCode}');
  }

  /// Members Grabber - Get Groups
  Future<List<dynamic>> getGroups() async {
    await init();
    final response = await http.get(
      Uri.parse('$baseUrl/api/members-grabber/groups'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Get groups failed: ${response.statusCode}');
  }

  /// Members Grabber - Get Members from Group
  Future<List<dynamic>> getMembers(String jid) async {
    await init();
    final response = await http.get(
      Uri.parse('$baseUrl/api/members-grabber/groups/$jid/members'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Get members failed: ${response.statusCode}');
  }

  /// Cloud Hub - Get Status
  Future<Map<String, dynamic>> getCloudStatus() async {
    await init();
    final response = await http.get(
      Uri.parse('$baseUrl/api/wa-hub/status'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Get status failed: ${response.statusCode}');
  }

  /// Cloud Hub - Chat with AI
  Future<Map<String, dynamic>> chatWithAI(String message) async {
    await init();
    final response = await http.post(
      Uri.parse('$baseUrl/api/wa-hub/chat'),
      headers: _headers,
      body: json.encode({'message': message}),
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Chat failed: ${response.statusCode}');
  }

  /// Cloud Hub - Fetch QR Code
  Future<Map<String, dynamic>> getQRCode() async {
    await init();
    final response = await http.get(
      Uri.parse('$baseUrl/api/wa-hub/qr'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Fetch QR failed: ${response.statusCode}');
  }

  /// Cloud Hub - Fetch Pairing Code
  Future<Map<String, dynamic>> getPairingCode(String phone) async {
    await init();
    final response = await http.get(
      Uri.parse('$baseUrl/api/wa-hub/pairing-code?phone=$phone'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Fetch Pairing Code failed: ${response.statusCode}');
  }

  /// Cloud Hub - Logout
  Future<Map<String, dynamic>> logout() async {
    await init();
    final response = await http.post(
      Uri.parse('$baseUrl/api/wa-hub/logout'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Logout failed: ${response.statusCode}');
  }

  /// Automation Hub - Get Instance Info
  Future<Map<String, dynamic>> getInstanceInfo() async {
    await init();
    final response = await http.get(
      Uri.parse('$baseUrl/api/automation-hub/instance'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Get instance info failed: ${response.statusCode}');
  }

  /// Automation Hub - Get Stats
  Future<Map<String, dynamic>> getStats() async {
    await init();
    final response = await http.get(
      Uri.parse('$baseUrl/api/automation-hub/stats'),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Get stats failed: ${response.statusCode}');
  }

  // --- NEW TOOLS INTEGRATION ---

  /// Account Warmer - Start
  Future<Map<String, dynamic>> startWarming({
    required String phone1,
    required String phone2,
    int count = 50,
    int delay = 60,
  }) async {
    await init();
    final response = await http.post(
      Uri.parse('$baseUrl/api/account-warmer/start'),
      headers: _headers,
      body: json.encode({
        'phone1': phone1,
        'phone2': phone2,
        'count': count,
        'delay': delay,
      }),
    );
    return json.decode(response.body);
  }

  /// Account Warmer - Stop
  Future<Map<String, dynamic>> stopWarming() async {
    await init();
    final response = await http.post(
      Uri.parse('$baseUrl/api/account-warmer/stop'),
      headers: _headers,
    );
    return json.decode(response.body);
  }

  /// Account Warmer - Logs
  Future<Map<String, dynamic>> getWarmingLogs() async {
    await init();
    final response = await http.get(
      Uri.parse('$baseUrl/api/account-warmer/logs'),
      headers: _headers,
    );
    return json.decode(response.body);
  }

  // --- CONNECTOR TOOLS (Track 2) ---

  /// Links Grabber - Hunt (Updated)
  Future<Map<String, dynamic>> startLinkHunt({
    required String keyword,
    int count = 10,
  }) async {
    await init();
    final response = await http.post(
      Uri.parse('$baseUrl/connector/grab_links'),
      headers: _headers,
      body: json.encode({'keyword': keyword, 'limit': count}),
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Link grab failed: ${response.statusCode}');
  }

  /// Auto Joiner - Start
  Future<Map<String, dynamic>> joinGroups({
    required List<String> links,
    int delay = 60,
    bool dryRun = true,
  }) async {
    await init();
    final response = await http.post(
      Uri.parse('$baseUrl/connector/join_groups'),
      headers: _headers,
      body: json.encode({'links': links, 'delay': delay, 'dry_run': dryRun}),
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Join groups failed: ${response.statusCode}');
  }

  /// Poll Sender - Send (Updated)
  Future<Map<String, dynamic>> sendPoll({
    required String jid,
    required String question,
    required List<String> options,
  }) async {
    await init();
    final response = await http.post(
      Uri.parse('$baseUrl/connector/send_poll'),
      headers: _headers,
      body: json.encode({'jid': jid, 'question': question, 'options': options}),
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Send poll failed: ${response.statusCode}');
  }

  // --- MARKET INTELLIGENCE (Track 1 & 3) ---

  /// Opportunity Hunter - Trigger
  Future<Map<String, dynamic>> triggerScan({
    required String type,
    required String keyword,
    int scrollingDepth = 2,
  }) async {
    await init();
    final uri = Uri.parse('$baseUrl/intelligence/trigger_scan').replace(
      queryParameters: {
        'type': type,
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
    String source = 'all',
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

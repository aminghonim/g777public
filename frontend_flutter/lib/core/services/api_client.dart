import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'package:g777_client/core/network/port_discovery.dart';

// --- Provider ---

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

// --- ApiClient ---

class ApiClient {
  static const String _tokenKey = 'jwt_token';
  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  static const String _baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );

  static const Duration _defaultTimeout = Duration(seconds: 15);

  // Dynamic Session State
  int? _dynamicPort;
  String? _handshakeToken;

  Future<void> _ensureInitialized() async {
    // If already have values, no need to re-initialize
    if (_dynamicPort != null && _handshakeToken != null) return;

    try {
      // Retry discovery to handle race conditions during backend startup
      for (int i = 0; i < 3; i++) {
        final session = await PortDiscovery.getActiveSession();
        if (session != null) {
          _dynamicPort = session['port'];
          _handshakeToken = session['token'];
          return;
        }
        await Future.delayed(const Duration(milliseconds: 500));
      }
    } catch (_) {}
  }

  Future<String> get resolvedBaseUrl async {
    await _ensureInitialized();
    if (_dynamicPort != null) {
      return 'http://127.0.0.1:$_dynamicPort';
    }
    return _baseUrl;
  }

  // --- Private header builder ---

  Future<Map<String, String>> _buildHeaders({
    Map<String, String>? extra,
  }) async {
    await _ensureInitialized();
    final token = await _storage.read(key: _tokenKey);
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    if (_handshakeToken != null) {
      headers['X-G777-Auth-Token'] = _handshakeToken!;
    }
    if (extra != null) headers.addAll(extra);
    return headers;
  }

  ApiResponse _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      final body = response.body.isNotEmpty ? jsonDecode(response.body) : null;
      return ApiResponse(data: body, statusCode: response.statusCode);
    }
    if (response.statusCode == 401) {
      // SAAS-005: Clear only authentication secrets while preserving system metadata
      _storage.delete(key: _tokenKey);
      _storage.delete(key: 'user_data');
      throw const ApiException(
        statusCode: 401,
        message: 'انتهت الجلسة. الرجاء تسجيل الدخول مجدداً.',
      );
    }
    if (response.statusCode == 403) {
      throw const ApiException(
        statusCode: 403,
        message: 'غير مصرح بهذه العملية.',
      );
    }
    // Generic server error
    String errorBody = 'Server error';
    if (response.body.isNotEmpty) {
      try {
        final decoded = jsonDecode(response.body);
        if (decoded is Map && decoded.containsKey('detail')) {
          errorBody = decoded['detail'].toString();
        } else {
          errorBody = response.body;
        }
      } catch (_) {
        errorBody = response.body;
      }
    }
    throw ApiException(statusCode: response.statusCode, message: errorBody);
  }

  // --- HTTP Methods ---

  Future<ApiResponse> get(
    String path, {
    Map<String, String>? queryParams,
    Map<String, String>? extraHeaders,
  }) async {
    final baseUrl = await resolvedBaseUrl;
    final uri = Uri.parse(
      '$baseUrl$path',
    ).replace(queryParameters: queryParams);
    final headers = await _buildHeaders(extra: extraHeaders);
    try {
      final response = await http
          .get(uri, headers: headers)
          .timeout(_defaultTimeout);
      return _handleResponse(response);
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(statusCode: 0, message: 'تعذر الاتصال: $e');
    }
  }

  Future<ApiResponse> post(
    String path, {
    Object? body,
    Map<String, String>? extraHeaders,
  }) async {
    final baseUrl = await resolvedBaseUrl;
    final uri = Uri.parse('$baseUrl$path');
    final headers = await _buildHeaders(extra: extraHeaders);
    try {
      final response = await http
          .post(
            uri,
            headers: headers,
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(_defaultTimeout);
      return _handleResponse(response);
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(statusCode: 0, message: 'تعذر الاتصال: $e');
    }
  }

  Future<ApiResponse> put(
    String path, {
    Object? body,
    Map<String, String>? extraHeaders,
  }) async {
    final baseUrl = await resolvedBaseUrl;
    final uri = Uri.parse('$baseUrl$path');
    final headers = await _buildHeaders(extra: extraHeaders);
    try {
      final response = await http
          .put(
            uri,
            headers: headers,
            body: body != null ? jsonEncode(body) : null,
          )
          .timeout(_defaultTimeout);
      return _handleResponse(response);
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(statusCode: 0, message: 'تعذر الاتصال: $e');
    }
  }

  Future<ApiResponse> delete(
    String path, {
    Map<String, String>? extraHeaders,
  }) async {
    final baseUrl = await resolvedBaseUrl;
    final uri = Uri.parse('$baseUrl$path');
    final headers = await _buildHeaders(extra: extraHeaders);
    try {
      final response = await http
          .delete(uri, headers: headers)
          .timeout(_defaultTimeout);
      return _handleResponse(response);
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(statusCode: 0, message: 'تعذر الاتصال: $e');
    }
  }

  // --- Multipart Upload ---

  Future<ApiResponse> multipartPost(
    String path, {
    required Map<String, String> fields,
    required String filePath,
    String fileField = 'file',
  }) async {
    final baseUrl = await resolvedBaseUrl;
    final uri = Uri.parse('$baseUrl$path');
    final headers = await _buildHeaders();

    try {
      final request = http.MultipartRequest('POST', uri);
      request.headers.addAll(headers);
      request.fields.addAll(fields);
      request.files.add(await http.MultipartFile.fromPath(fileField, filePath));

      final streamedResponse = await request.send().timeout(
        const Duration(seconds: 60),
      );
      final response = await http.Response.fromStream(streamedResponse);
      return _handleResponse(response);
    } catch (e) {
      throw ApiException(statusCode: 0, message: 'تعذر رفع الملف: $e');
    }
  }

  // --- SSE Stream Observer ---

  Stream<Map<String, dynamic>> streamGet(String path) async* {
    final baseUrl = await resolvedBaseUrl;
    final uri = Uri.parse('$baseUrl$path');
    final headers = await _buildHeaders();

    final client = http.Client();
    final request = http.Request('GET', uri);
    request.headers.addAll(headers);

    try {
      final response = await client.send(request);
      if (response.statusCode != 200) {
        throw ApiException(
          statusCode: response.statusCode,
          message: 'فشل بدء قناة البيانات المباشرة',
        );
      }

      await for (final line
          in response.stream
              .transform(utf8.decoder)
              .transform(const LineSplitter())) {
        if (line.trim().isEmpty) continue;
        if (line.startsWith('data: ')) {
          final data = line.substring(6);
          try {
            yield jsonDecode(data) as Map<String, dynamic>;
          } catch (_) {
            // Skip malformed SSE chunks
          }
        }
      }
    } finally {
      client.close();
    }
  }
}

// --- Response Model ---

class ApiResponse {
  final dynamic data;
  final int statusCode;

  const ApiResponse({required this.data, required this.statusCode});

  bool get isSuccess => statusCode >= 200 && statusCode < 300;
}

// --- Exception Model ---

class ApiException implements Exception {
  final int statusCode;
  final String message;

  const ApiException({required this.statusCode, required this.message});

  @override
  String toString() => 'ApiException($statusCode): $message';
}

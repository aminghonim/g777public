import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../config/env_config.dart';
import '../security/secure_storage_service.dart';
import 'port_discovery.dart';
import 'session_provider.dart';
import '../../features/auth/providers/auth_provider.dart';

part 'dio_provider.g.dart';

@riverpod
Future<Dio> dio(Ref ref) async {
  final authState = await ref.watch(authProvider.future);
  final sessionState = ref.watch(sessionProvider);

  String baseUrl = EnvConfig.baseUrl;
  String? handshakeToken;

  if (sessionState.hasValue && sessionState.value != null) {
    final session = sessionState.value!;
    if (session.containsKey('port')) {
      baseUrl = 'http://127.0.0.1:${session['port']}';
    }
    handshakeToken = session['token'];
  } else {
    // Proactive Fallback (ASVS V7.4.1): Sync discovery if provider is late
    // This prevents the 401 -> Logout loop during high-latency startup
    try {
      final session = await PortDiscovery.getActiveSession();
      if (session != null) {
        if (session.containsKey('port')) {
          baseUrl = 'http://127.0.0.1:${session['port']}';
        }
        handshakeToken = session['token'];
      }
    } catch (_) {}
  }

  final options = BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 15),
    receiveTimeout: const Duration(seconds: 15),
    headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
  );

  final dio = Dio(options);

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        // SAAS-005: Inject JWT if authenticated or guest
        switch (authState) {
          case AuthAuthenticated(token: final token):
            options.headers['Authorization'] = 'Bearer $token';
          case AuthGuest(token: final token?) when token.isNotEmpty:
            options.headers['Authorization'] = 'Bearer $token';
          case _:
            break;
        }

        // Inject Session Handshake Token
        if (handshakeToken != null) {
          options.headers['X-G777-Auth-Token'] = handshakeToken;
        }

        // MCP-SEC-001: Inject MCP token from secure storage for backend tool calls.
        // The token is read at request time to always use the freshest value.
        final mcpToken = await SecureStorageService.read('mcp_token');
        if (mcpToken != null && mcpToken.isNotEmpty) {
          options.headers['X-MCP-Token'] = mcpToken;
        }

        return handler.next(options);
      },
      onError: (e, handler) async {
        final statusCode = e.response?.statusCode;

        // M5-SEC: 401 triggers full logout via Riverpod to update UI immediately
        if (statusCode == 401) {
          // Use Future.microtask to avoid calling ref.read during a provider transition
          Future.microtask(() {
  ref.invalidate(authProvider);
});
        }

        // QUOTA-SEC: 403 — distinguish between quota exhaustion and permission denial
        if (statusCode == 403) {
          final responseData = e.response?.data;
          final detail = _extractDetail(responseData);
          final isQuotaError = detail.toUpperCase().contains('QUOTA') ||
              detail.toUpperCase().contains('LIMIT');

          final enrichedError = DioException(
            requestOptions: e.requestOptions,
            response: e.response,
            type: e.type,
            error: isQuotaError
                ? 'QUOTA_EXCEEDED:$detail'
                : 'FORBIDDEN:$detail',
          );
          return handler.next(enrichedError);
        }

        return handler.next(e);
      },
    ),
  );

  return dio;
}

/// Safely extracts a detail message from an API error response body.
String _extractDetail(dynamic responseData) {
  try {
    if (responseData is Map) {
      final detail = responseData['detail'];
      if (detail is String) return detail;
      if (detail is Map) return detail['message']?.toString() ?? '';
    }
  } catch (_) {}
  return '';
}

import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../config/env_config.dart';
import 'port_discovery.dart';
import 'session_provider.dart';
import '../../features/auth/providers/auth_provider.dart';

part 'dio_provider.g.dart';

@riverpod
Future<Dio> dio(DioRef ref) async {
  final authState = await ref.watch(authProvider.future);
  final sessionState = ref.watch(sessionProvider);

  String baseUrl = EnvConfig.baseUrl;
  String? handshakeToken;

  if (sessionState.hasValue && sessionState.value != null) {
    final session = sessionState.value!;
    if (session.containsKey('port')) {
      // Route through Nginx (Port 80) for Docker support
      baseUrl = 'http://127.0.0.1';
    }
    handshakeToken = session['token'];
  } else {
    // Proactive Fallback (ASVS V7.4.1): Sync discovery if provider is late
    // This prevents the 401 -> Logout loop during high-latency startup
    try {
      final session = await PortDiscovery.getActiveSession();
      if (session != null) {
        if (session.containsKey('port')) {
          // Route through Nginx (Port 80) for Docker support
          baseUrl = 'http://127.0.0.1';
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
      onRequest: (options, handler) {
        // SAAS-005: Inject JWT if authenticated or guest
        if (authState is AuthAuthenticated) {
          options.headers['Authorization'] = 'Bearer ${authState.token}';
        } else if (authState is AuthGuest && authState.token != null) {
          options.headers['Authorization'] = 'Bearer ${authState.token}';
        }

        // Inject Handshake Token
        if (handshakeToken != null) {
          options.headers['X-G777-Auth-Token'] = handshakeToken;
        }

        return handler.next(options);
      },
      onError: (e, handler) {
        // SAAS-005: Global 401 Logout
        if (e.response?.statusCode == 401) {
          ref.read(authProvider.notifier).logout();
        }
        return handler.next(e);
      },
    ),
  );

  return dio;
}

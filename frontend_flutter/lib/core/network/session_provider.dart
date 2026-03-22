import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'port_discovery.dart';

part 'session_provider.g.dart';

@Riverpod(keepAlive: true)
class Session extends _$Session {
  @override
  FutureOr<Map<String, dynamic>?> build() async {
    // Retry up to 5 times with a small delay to handle backend restarts
    for (int i = 0; i < 5; i++) {
      final session = await PortDiscovery.getActiveSession();
      if (session != null) return session;
      await Future.delayed(Duration(milliseconds: 500 * (i + 1)));
    }
    return null;
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      for (int i = 0; i < 3; i++) {
        final session = await PortDiscovery.getActiveSession();
        if (session != null) return session;
        await Future.delayed(const Duration(milliseconds: 500));
      }
      return null;
    });
  }
}

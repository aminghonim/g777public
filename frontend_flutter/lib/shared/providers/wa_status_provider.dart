import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/api_client.dart';

final waStatusProvider = NotifierProvider<WAStatusNotifier, WAStatus>(
  WAStatusNotifier.new,
);

class WAStatus {
  final bool isConnected;
  final Map<String, dynamic>? details;
  final bool isLoading;
  final String? error;

  const WAStatus({
    this.isConnected = false,
    this.details,
    this.isLoading = false,
    this.error,
  });

  WAStatus copyWith({
    bool? isConnected,
    Map<String, dynamic>? details,
    bool? isLoading,
    String? error,
  }) {
    return WAStatus(
      isConnected: isConnected ?? this.isConnected,
      details: details ?? this.details,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

class WAStatusNotifier extends Notifier<WAStatus> {
  Timer? _timer;

  @override
  WAStatus build() {
    final apiClient = ref.watch(apiClientProvider);
    ref.onDispose(() => _timer?.cancel());

    Future.microtask(() => _refreshStatus(apiClient));
    _timer = Timer.periodic(
      const Duration(seconds: 10),
      (_) => _refreshStatus(apiClient),
    );

    return const WAStatus();
  }

  ApiClient get _apiClient => ref.read(apiClientProvider);

  Future<void> _refreshStatus(ApiClient apiClient) async {
    try {
      final response = await apiClient.get('/api/wa-hub/status');
      if (response.isSuccess) {
        state = state.copyWith(
          isConnected: response.data['is_connected'] ?? false,
          details: response.data['details'],
          isLoading: false,
          error: null,
        );
      } else {
        state = state.copyWith(isLoading: false);
      }
    } catch (e) {
      state = state.copyWith(
        isConnected: false,
        error: e.toString(),
        isLoading: false,
      );
    }
  }

  Future<void> refreshStatus() async {
    return _refreshStatus(_apiClient);
  }

  Future<void> logout() async {
    state = state.copyWith(isLoading: true);
    try {
      await _apiClient.post('/api/wa-hub/logout');
      await refreshStatus();
    } catch (e) {
      state = state.copyWith(isLoading: false, isConnected: false);
    }
  }
}

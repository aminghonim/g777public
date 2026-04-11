import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/api_client.dart';

final waStatusProvider = StateNotifierProvider<WAStatusNotifier, WAStatus>((
  ref,
) {
  final apiClient = ref.watch(apiClientProvider);
  return WAStatusNotifier(apiClient);
});

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

class WAStatusNotifier extends StateNotifier<WAStatus> {
  final ApiClient _apiClient;
  Timer? _timer;

  WAStatusNotifier(this._apiClient) : super(const WAStatus()) {
    refreshStatus();
    _timer = Timer.periodic(
      const Duration(seconds: 10),
      (_) => refreshStatus(),
    );
  }

  Future<void> refreshStatus() async {
    try {
      final response = await _apiClient.get('/api/wa-hub/status');
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

  Future<void> logout() async {
    state = state.copyWith(isLoading: true);
    try {
      await _apiClient.post('/api/wa-hub/logout');
      await refreshStatus();
    } catch (e) {
      state = state.copyWith(isLoading: false, isConnected: false);
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}

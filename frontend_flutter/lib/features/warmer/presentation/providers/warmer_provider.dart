import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/api_client.dart';

/// Warmer Configuration State
class WarmerState {
  final bool isLoading;
  final bool isActive;
  final int dailyLimit;
  final int delayMin;
  final int delayMax;
  final List<String> selectedBots;
  final List<String> availableBots;
  final String? error;
  final String? successMessage;

  const WarmerState({
    this.isLoading = false,
    this.isActive = false,
    this.dailyLimit = 100,
    this.delayMin = 30,
    this.delayMax = 120,
    this.selectedBots = const [],
    this.availableBots = const [],
    this.error,
    this.successMessage,
  });

  WarmerState copyWith({
    bool? isLoading,
    bool? isActive,
    int? dailyLimit,
    int? delayMin,
    int? delayMax,
    List<String>? selectedBots,
    List<String>? availableBots,
    String? error,
    String? successMessage,
  }) {
    return WarmerState(
      isLoading: isLoading ?? this.isLoading,
      isActive: isActive ?? this.isActive,
      dailyLimit: dailyLimit ?? this.dailyLimit,
      delayMin: delayMin ?? this.delayMin,
      delayMax: delayMax ?? this.delayMax,
      selectedBots: selectedBots ?? this.selectedBots,
      availableBots: availableBots ?? this.availableBots,
      error: error ?? this.error,
      successMessage: successMessage ?? this.successMessage,
    );
  }
}

/// Warmer Notifier (Riverpod 3)
class WarmerNotifier extends Notifier<WarmerState> {
  @override
  WarmerState build() => const WarmerState();

  ApiClient get _api => ref.read(apiClientProvider);

  Future<void> loadConfiguration() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final res = await _api.get('/api/warmer/config');
      if (res.isSuccess) {
        final data = res.data as Map<String, dynamic>;
        state = state.copyWith(
          isLoading: false,
          isActive: data['is_active'] ?? false,
          dailyLimit: data['daily_limit'] ?? 100,
          delayMin: data['delay_min'] ?? 30,
          delayMax: data['delay_max'] ?? 120,
          selectedBots: List<String>.from(data['selected_bots'] ?? []),
          availableBots: List<String>.from(data['available_bots'] ?? []),
        );
      } else {
        throw Exception('Failed to load warmer configuration');
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load configuration: $e',
      );
    }
  }

  Future<void> saveConfiguration() async {
    state = state.copyWith(isLoading: true, error: null, successMessage: null);
    try {
      final body = {
        'is_active': state.isActive,
        'daily_limit': state.dailyLimit,
        'delay_min': state.delayMin,
        'delay_max': state.delayMax,
        'selected_bots': state.selectedBots,
      };

      final res = await _api.post('/api/warmer/config', body: body);

      if (res.isSuccess) {
        state = state.copyWith(
          isLoading: false,
          successMessage: 'Warmer configuration saved successfully',
        );
      } else {
        throw Exception(res.data?['error'] ?? 'Failed to save configuration');
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to save configuration: $e',
      );
    }
  }

  void toggleActive() {
    state = state.copyWith(isActive: !state.isActive);
  }

  void setDailyLimit(int limit) {
    state = state.copyWith(dailyLimit: limit);
  }

  void setDelayRange(int min, int max) {
    state = state.copyWith(delayMin: min, delayMax: max);
  }

  void toggleBot(String botId) {
    final currentSelection = List<String>.from(state.selectedBots);
    if (currentSelection.contains(botId)) {
      currentSelection.remove(botId);
    } else {
      currentSelection.add(botId);
    }
    state = state.copyWith(selectedBots: currentSelection);
  }

  void selectAllBots() {
    state = state.copyWith(
      selectedBots: List<String>.from(state.availableBots),
    );
  }

  void deselectAllBots() {
    state = state.copyWith(selectedBots: const []);
  }

  void clearError() {
    state = state.copyWith(error: null);
  }

  void clearSuccessMessage() {
    state = state.copyWith(successMessage: null);
  }
}

/// Warmer Provider
final warmerProvider = NotifierProvider<WarmerNotifier, WarmerState>(
  WarmerNotifier.new,
);

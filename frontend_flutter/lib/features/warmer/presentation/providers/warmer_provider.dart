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

/// Warmer StateNotifier
class WarmerNotifier extends StateNotifier<WarmerState> {
  final Ref ref;

  WarmerNotifier(this.ref) : super(const WarmerState());

  ApiClient get _api => ref.read(apiClientProvider);

  /// Load available bots and current configuration
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

  /// Save warmer configuration to backend
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

  /// Toggle warmer active state
  void toggleActive() {
    state = state.copyWith(isActive: !state.isActive);
  }

  /// Update daily limit
  void setDailyLimit(int limit) {
    state = state.copyWith(dailyLimit: limit);
  }

  /// Update delay range
  void setDelayRange(int min, int max) {
    state = state.copyWith(delayMin: min, delayMax: max);
  }

  /// Toggle bot selection
  void toggleBot(String botId) {
    final currentSelection = List<String>.from(state.selectedBots);
    if (currentSelection.contains(botId)) {
      currentSelection.remove(botId);
    } else {
      currentSelection.add(botId);
    }
    state = state.copyWith(selectedBots: currentSelection);
  }

  /// Select all bots
  void selectAllBots() {
    state = state.copyWith(
      selectedBots: List<String>.from(state.availableBots),
    );
  }

  /// Deselect all bots
  void deselectAllBots() {
    state = state.copyWith(selectedBots: const []);
  }

  /// Clear error message
  void clearError() {
    state = state.copyWith(error: null);
  }

  /// Clear success message
  void clearSuccessMessage() {
    state = state.copyWith(successMessage: null);
  }
}

/// Warmer Provider
final warmerProvider = StateNotifierProvider<WarmerNotifier, WarmerState>((
  ref,
) {
  return WarmerNotifier(ref);
});

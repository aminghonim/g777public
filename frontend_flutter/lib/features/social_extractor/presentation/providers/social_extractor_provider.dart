import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/api_service.dart';

/// Social Extractor Repository Provider
final socialExtractorRepositoryProvider = Provider<SocialExtractorRepository>((ref) {
  return SocialExtractorRepository(apiService: ApiService());
});

/// Social Extractor State
class SocialExtractorState {
  final bool isLoading;
  final List<Map<String, dynamic>> results;
  final String? error;
  final bool isScanning;
  final String? scanMessage;
  final List<String> logs;
  final String selectedPlatform;

  const SocialExtractorState({
    this.isLoading = false,
    this.results = const [],
    this.error,
    this.isScanning = false,
    this.scanMessage,
    this.logs = const [],
    this.selectedPlatform = 'all',
  });

  SocialExtractorState copyWith({
    bool? isLoading,
    List<Map<String, dynamic>>? results,
    String? error,
    bool? isScanning,
    String? scanMessage,
    List<String>? logs,
    String? selectedPlatform,
  }) {
    return SocialExtractorState(
      isLoading: isLoading ?? this.isLoading,
      results: results ?? this.results,
      error: error ?? this.error,
      isScanning: isScanning ?? this.isScanning,
      scanMessage: scanMessage ?? this.scanMessage,
      logs: logs ?? this.logs,
      selectedPlatform: selectedPlatform ?? this.selectedPlatform,
    );
  }
}

/// Social Extractor Notifier
class SocialExtractorNotifier extends StateNotifier<SocialExtractorState> {
  final SocialExtractorRepository _repository;

  SocialExtractorNotifier(this._repository) : super(const SocialExtractorState());

  /// Load existing social results
  Future<void> loadResults() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final results = await _repository.getSocialResults();
      state = state.copyWith(
        isLoading: false,
        results: results,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Trigger a new social scan
  Future<void> triggerScan(String keyword, {int scrollingDepth = 2}) async {
    state = state.copyWith(isScanning: true, error: null, logs: []);
    _addLog('Starting social media scan for: $keyword');
    
    try {
      final response = await _repository.triggerSocialScan(
        keyword: keyword,
        scrollingDepth: scrollingDepth,
      );
      
      _addLog('Scan queued: ${response['message']}');
      _addLog('ETA: ${response['eta']}');
      
      state = state.copyWith(
        isScanning: false,
        scanMessage: response['message'] as String?,
      );
      
      // Simulate progressive log updates
      await _simulateProgressiveLogs();
      
      // Reload results after a delay
      await Future.delayed(const Duration(seconds: 3));
      _addLog('Reloading results...');
      await loadResults();
      _addLog('Scan complete. Found ${state.results.length} results.');
    } catch (e) {
      _addLog('Error: $e', isError: true);
      state = state.copyWith(
        isScanning: false,
        error: e.toString(),
      );
    }
  }

  void _addLog(String message, {bool isError = false}) {
    final prefix = isError ? '[ERROR]' : '[INFO]';
    final timestamp = DateTime.now().toString().split('.').first;
    final logEntry = '[$timestamp] $prefix $message';
    
    state = state.copyWith(
      logs: [logEntry, ...state.logs].take(100).toList(),
    );
  }

  Future<void> _simulateProgressiveLogs() async {
    await Future.delayed(const Duration(seconds: 1));
    _addLog('Initializing scraper...');
    await Future.delayed(const Duration(seconds: 1));
    _addLog('Connecting to social platforms...');
    await Future.delayed(const Duration(seconds: 2));
    _addLog('Scanning for keyword matches...');
    await Future.delayed(const Duration(seconds: 2));
    _addLog('Extracting profile data...');
  }

  void setPlatform(String platform) {
    state = state.copyWith(selectedPlatform: platform);
  }

  void clearError() {
    state = state.copyWith(error: null);
  }

  void clearScanMessage() {
    state = state.copyWith(scanMessage: null);
  }

  void clearLogs() {
    state = state.copyWith(logs: const []);
  }
}

/// Social Extractor Notifier Provider
final socialExtractorProvider = StateNotifierProvider<SocialExtractorNotifier, SocialExtractorState>((ref) {
  final repository = ref.watch(socialExtractorRepositoryProvider);
  return SocialExtractorNotifier(repository);
});

/// Social Extractor Repository
class SocialExtractorRepository {
  final ApiService _apiService;

  SocialExtractorRepository({required ApiService apiService})
      : _apiService = apiService;

  /// Get existing social results
  Future<List<Map<String, dynamic>>> getSocialResults() async {
    final response = await _apiService.getOpportunities(source: 'social');
    final results = response['results'] as List<dynamic>?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  /// Trigger a new social scan
  Future<Map<String, dynamic>> triggerSocialScan({
    required String keyword,
    int scrollingDepth = 2,
  }) async {
    return await _apiService.triggerScan(
      type: 'social',
      keyword: keyword,
      scrollingDepth: scrollingDepth,
    );
  }
}

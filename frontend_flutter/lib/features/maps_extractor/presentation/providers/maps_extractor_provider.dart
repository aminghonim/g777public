import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/api_service.dart';

/// Maps Extractor Repository Provider
final mapsExtractorRepositoryProvider =
    Provider<MapsExtractorRepository>((ref) {
  return MapsExtractorRepository(apiService: ApiService());
});

/// Maps Extractor State
class MapsExtractorState {
  final bool isLoading;
  final List<Map<String, dynamic>> results;
  final String? error;
  final bool isScanning;
  final String? scanMessage;

  const MapsExtractorState({
    this.isLoading = false,
    this.results = const [],
    this.error,
    this.isScanning = false,
    this.scanMessage,
  });

  MapsExtractorState copyWith({
    bool? isLoading,
    List<Map<String, dynamic>>? results,
    String? error,
    bool? isScanning,
    String? scanMessage,
  }) {
    return MapsExtractorState(
      isLoading: isLoading ?? this.isLoading,
      results: results ?? this.results,
      error: error ?? this.error,
      isScanning: isScanning ?? this.isScanning,
      scanMessage: scanMessage ?? this.scanMessage,
    );
  }
}

/// Maps Extractor Notifier (Riverpod 3)
class MapsExtractorNotifier extends Notifier<MapsExtractorState> {
  @override
  MapsExtractorState build() => const MapsExtractorState();

  MapsExtractorRepository get _repository =>
      ref.read(mapsExtractorRepositoryProvider);

  Future<void> loadResults() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final results = await _repository.getMapsResults();
      state = state.copyWith(isLoading: false, results: results);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> triggerScan(
    String query,
    String location, {
    int scrollingDepth = 2,
  }) async {
    state = state.copyWith(isScanning: true, error: null);
    try {
      final keyword = '$query in $location';
      final response = await _repository.triggerMapsScan(
        keyword: keyword,
        scrollingDepth: scrollingDepth,
      );
      state = state.copyWith(
        isScanning: false,
        scanMessage: response['message'] as String?,
      );
      await Future.delayed(const Duration(seconds: 3));
      await loadResults();
    } catch (e) {
      state = state.copyWith(isScanning: false, error: e.toString());
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }

  void clearScanMessage() {
    state = state.copyWith(scanMessage: null);
  }
}

/// Maps Extractor Notifier Provider
final mapsExtractorProvider =
    NotifierProvider<MapsExtractorNotifier, MapsExtractorState>(
  MapsExtractorNotifier.new,
);

/// Maps Extractor Repository
class MapsExtractorRepository {
  final ApiService _apiService;

  MapsExtractorRepository({required ApiService apiService})
      : _apiService = apiService;

  Future<List<Map<String, dynamic>>> getMapsResults() async {
    final response = await _apiService.getOpportunities(source: 'maps');
    final results = response['results'] as List<dynamic>?;
    return results?.cast<Map<String, dynamic>>() ?? [];
  }

  Future<Map<String, dynamic>> triggerMapsScan({
    required String keyword,
    int scrollingDepth = 2,
  }) async {
    return await _apiService.triggerScan(
      type: 'maps',
      keyword: keyword,
      scrollingDepth: scrollingDepth,
    );
  }
}

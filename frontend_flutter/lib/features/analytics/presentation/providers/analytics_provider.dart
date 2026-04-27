import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:g777_client/features/analytics/data/models/analytics_model.dart';
import 'package:g777_client/features/analytics/data/repositories/analytics_repository.dart';

part 'analytics_provider.g.dart';

@riverpod
class Analytics extends _$Analytics {
  @override
  FutureOr<AnalyticsModel> build() async {
    return _fetch();
  }

  Future<AnalyticsModel> _fetch() async {
    final repository = await ref.read(analyticsRepositoryProvider.future);
    return repository.getDashboardAnalytics();
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetch());
  }
}

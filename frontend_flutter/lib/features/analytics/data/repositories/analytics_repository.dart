import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:g777_client/core/network/dio_provider.dart';
import 'package:g777_client/features/analytics/data/models/analytics_model.dart';

part 'analytics_repository.g.dart';

class AnalyticsRepository {
  final Dio _dio;

  AnalyticsRepository(this._dio);

  Future<AnalyticsModel> getDashboardAnalytics() async {
    try {
      final response = await _dio.get('/analytics/dashboard');
      return AnalyticsModel.fromJson(response.data);
    } on DioException catch (e) {
      throw Exception(
        e.response?.data['detail'] ?? 'Failed to fetch analytics',
      );
    }
  }
}

@riverpod
Future<AnalyticsRepository> analyticsRepository(Ref ref) async {
  final dio = await ref.watch(dioProvider.future);
  return AnalyticsRepository(dio);
}

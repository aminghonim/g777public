import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/network/dio_provider.dart';

part 'evolution_service.g.dart';

class EvolutionException implements Exception {
  final String message;
  final int? statusCode;

  EvolutionException(this.message, {this.statusCode});

  @override
  String toString() => 'EvolutionException: $message';
}

class EvolutionService {
  final Dio _dio;

  EvolutionService(this._dio);

  /// SAAS-011: Request dynamic provisioning of a WhatsApp instance.
  Future<Map<String, dynamic>> createInstance() async {
    try {
      final response = await _dio.post('/evolution/create');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// SAAS-011: Retrieve a fresh QR code for an existing instance.
  Future<Map<String, dynamic>> getQRCode() async {
    try {
      final response = await _dio.get('/evolution/qr');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// SAAS-011: Check the current connection state of the instance.
  Future<Map<String, dynamic>> getStatus() async {
    try {
      final response = await _dio.get('/evolution/status');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// SAAS-011: Delete and unlink the instance from this tenant.
  Future<void> deleteInstance() async {
    try {
      await _dio.delete('/evolution/delete');
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  EvolutionException _handleError(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.connectionError) {
      return EvolutionException(
        'Network connection error. Please check your internet connection.',
      );
    }

    final data = e.response?.data;
    String message = 'An error occurred with WhatsApp integration.';

    if (data is Map<String, dynamic>) {
      message = data['detail']?.toString() ?? message;
    }

    return EvolutionException(message, statusCode: e.response?.statusCode);
  }
}

@riverpod
Future<EvolutionService> evolutionService(Ref ref) async {
  final dio = await ref.watch(dioProvider.future);
  return EvolutionService(dio);
}

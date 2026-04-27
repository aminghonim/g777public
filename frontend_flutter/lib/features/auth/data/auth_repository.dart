import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/network/dio_provider.dart';

part 'auth_repository.g.dart';

class AuthException implements Exception {
  final String message;
  final int? statusCode;

  AuthException(this.message, {this.statusCode});

  @override
  String toString() => 'AuthException: $message';
}

class AuthRepository {
  final Dio _dio;

  AuthRepository(this._dio);

  /// Authenticates user against the Cloud Backend.
  /// Returns a Map containing 'token' and 'user' data.
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await _dio.post(
        '/auth/login',
        data: {
          'username':
              email, // Backend expects 'username' for OAuth2 compatibility usually
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;
        // Verify payload structure matches expectations
        if (data is Map<String, dynamic> && data.containsKey('access_token')) {
          return {
            'token': data['access_token'],
            'user': data['user'] ?? {'email': email},
          };
        }
        throw AuthException('Invalid response format from server');
      }

      throw AuthException('Unexpected error occurred');
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw AuthException('Invalid email or password');
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.connectionError) {
        throw AuthException(
          'Network connection error. Please check your internet.',
        );
      }

      final errorMessage =
          e.response?.data?['detail'] ??
          'Authentication failed. Please try again.';
      throw AuthException(errorMessage.toString());
    } catch (e) {
      throw AuthException('An unknown error occurred: $e');
    }
  }

  /// Fetches a guest token from the backend for trial periods.
  Future<Map<String, dynamic>> guestLogin() async {
    try {
      final response = await _dio.post('/auth/license/guest');

      if (response.statusCode == 200) {
        final data = response.data;
        if (data is Map<String, dynamic> && data.containsKey('access_token')) {
          return {
            'token': data['access_token'],
            'user': {'username': 'Trial Guest', 'role': 'guest'},
          };
        }
        throw AuthException(
          'Invalid response format from server for guest token',
        );
      }

      throw AuthException('Unexpected error occurred during guest activation');
    } on DioException catch (e) {
      final errorMessage =
          e.response?.data?['detail'] ??
          'Guest authentication failed. Please check backend connection.';
      throw AuthException(errorMessage.toString());
    } catch (e) {
      throw AuthException('An unknown error occurred: $e');
    }
  }
}

@riverpod
Future<AuthRepository> authRepository(Ref ref) async {
  final dio = await ref.watch(dioProvider.future);
  return AuthRepository(dio);
}

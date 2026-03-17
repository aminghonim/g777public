import 'dart:async';
import 'dart:convert';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../data/auth_repository.dart';
import '../../../core/security/secure_storage_service.dart';
import '../../../core/services/clerk_auth_service.dart';

part 'auth_provider.g.dart';

/// Sealed class representing the logical Authentication States.
sealed class AuthState {
  const AuthState();
}

class AuthUnauthenticated extends AuthState {
  final int trialDaysRemaining;
  const AuthUnauthenticated({this.trialDaysRemaining = 14});
}

class AuthAuthenticated extends AuthState {
  final String token;
  final Map<String, dynamic> user;
  const AuthAuthenticated({required this.token, required this.user});
}

class AuthGuest extends AuthState {
  final int trialDaysRemaining;
  final String? token;
  const AuthGuest({this.trialDaysRemaining = 14, this.token});
}

class AuthError extends AuthState {
  final String message;
  const AuthError(this.message);
}

@riverpod
class Auth extends _$Auth {
  static const int _trialDaysTarget = 14;

  @override
  FutureOr<AuthState> build() async {
    int remainingDays = await _calculateTrialDays();

    try {
      final token = await SecureStorageService.read('jwt_token');
      final userStr = await SecureStorageService.read('user_data');
      if (token != null && userStr != null) {
        final user = jsonDecode(userStr);
        if (user['role'] == 'guest') {
          return AuthGuest(trialDaysRemaining: remainingDays, token: token);
        }
        return AuthAuthenticated(token: token, user: user);
      }
    } catch (e) {
      // Ignore errors on load, fall back to Unauthenticated
    }
    return AuthUnauthenticated(trialDaysRemaining: remainingDays);
  }

  Future<int> _calculateTrialDays() async {
    try {
      final firstLaunchStr = await SecureStorageService.read(
        'first_launch_date',
      );
      DateTime firstLaunch;

      if (firstLaunchStr == null) {
        firstLaunch = DateTime.now();
        await SecureStorageService.write(
          'first_launch_date',
          firstLaunch.toIso8601String(),
        );
      } else {
        firstLaunch = DateTime.parse(firstLaunchStr);
      }

      final diff = DateTime.now().difference(firstLaunch).inDays;
      final remaining = _trialDaysTarget - diff;
      return remaining < 0 ? 0 : remaining;
    } catch (e) {
      return 0; // Fallback to expired if error parsing dates
    }
  }

  /// Cloud Sync Entry Point
  Future<bool> login(String email, String password) async {
    state = const AsyncLoading();
    try {
      final repository = await ref.read(authRepositoryProvider.future);
      final result = await repository.login(email, password);

      final token = result['token'] as String;
      final user = result['user'] as Map<String, dynamic>;

      await SecureStorageService.write('jwt_token', token);
      await SecureStorageService.write('user_data', jsonEncode(user));

      state = AsyncData(AuthAuthenticated(token: token, user: user));
      return true;
    } on AuthException catch (e) {
      state = AsyncData(AuthError(e.message));
      return false;
    } catch (e) {
      state = const AsyncData(AuthError('An unexpected error occurred.'));
      return false;
    }
  }

  /// Local-Only Entry Point (Zero Friction)
  Future<bool> continueAsGuest() async {
    state = const AsyncLoading();
    int remainingDays = await _calculateTrialDays();
    if (remainingDays <= 0) {
      state = const AsyncData(AuthUnauthenticated(trialDaysRemaining: 0));
      return false;
    }

    try {
      final repository = await ref.read(authRepositoryProvider.future);
      final result = await repository.guestLogin();

      final token = result['token'] as String;
      final user = result['user'] as Map<String, dynamic>;

      await SecureStorageService.write('jwt_token', token);
      await SecureStorageService.write('user_data', jsonEncode(user));

      state = AsyncData(
        AuthGuest(trialDaysRemaining: remainingDays, token: token),
      );
      return true;
    } catch (e) {
      state = const AsyncData(AuthError('Failed to activate trial session'));
      return false;
    }
  }

  /// Clerk Deep-Link Entry Point (Windows Desktop — RFC 8252 Loopback flow).
  /// Opens the system browser to Clerk's hosted sign-in page and waits for
  /// the token to arrive via a local HTTP callback server on a random port.
  Future<bool> loginWithClerk() async {
    state = const AsyncLoading();
    try {
      final token = await ClerkAuthService.signIn();
      await ClerkAuthService.saveToken(token);

      // Store under the same keys as the legacy login for router compatibility.
      await SecureStorageService.write('jwt_token', token);
      await SecureStorageService.write(
        'user_data',
        '{"role":"client","auth_method":"clerk"}',
      );

      state = AsyncData(
        AuthAuthenticated(token: token, user: const {'auth_method': 'clerk'}),
      );
      return true;
    } on ClerkAuthException catch (e) {
      state = AsyncData(AuthError(e.message));
      return false;
    } catch (e) {
      state = AsyncData(AuthError('Clerk sign-in failed: $e'));
      return false;
    }
  }

  Future<void> logout() async {
    state = const AsyncLoading();
    // SAAS-005: Clear authentication secrets while preserving system metadata
    await SecureStorageService.delete('jwt_token');
    await SecureStorageService.delete('user_data');
    state = const AsyncData(AuthUnauthenticated());
  }
}

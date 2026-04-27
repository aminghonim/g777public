import 'dart:async';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/services/api_client.dart';
import '../../../core/security/secure_storage_service.dart';

part 'license_status_provider.g.dart';

/// Represents the current license status from the backend.
class LicenseStatus {
  final bool isValid;
  final String reason;
  final String? role;
  final String? expiresAt;
  final int? daysRemaining;
  final int? daysExpired;

  const LicenseStatus({
    required this.isValid,
    required this.reason,
    this.role,
    this.expiresAt,
    this.daysRemaining,
    this.daysExpired,
  });

  factory LicenseStatus.fromJson(Map<String, dynamic> json) {
    return LicenseStatus(
      isValid: json['is_valid'] as bool? ?? true,
      reason: json['reason'] as String? ?? 'unknown',
      role: json['role'] as String?,
      expiresAt: json['expires_at'] as String?,
      daysRemaining: json['days_remaining'] as int?,
      daysExpired: json['days_expired'] as int?,
    );
  }

  /// Whether the subscription is approaching expiry (7 days or less).
  bool get isExpiringSoon {
    if (daysRemaining == null) return false;
    return daysRemaining! >= 0 && daysRemaining! <= 7;
  }

  /// Whether the license has expired or been deactivated.
  bool get isExpired => !isValid;

  /// Whether this is a guest user (no license binding).
  bool get isGuest => role == 'guest';

  /// Human-readable remaining time text.
  String get remainingText {
    if (daysRemaining == null) return '';
    if (daysRemaining! <= 0) return 'EXPIRED';
    if (daysRemaining! == 1) return '1 day';
    return '$daysRemaining days';
  }

  static const LicenseStatus unknown = LicenseStatus(
    isValid: true,
    reason: 'unknown',
  );

  static const LicenseStatus noToken = LicenseStatus(
    isValid: true,
    reason: 'no_token',
    role: 'guest',
  );
}

@riverpod
class LicenseStatusNotifier extends _$LicenseStatusNotifier {
  @override
  FutureOr<LicenseStatus> build() async {
    return _fetchLicenseStatus();
  }

  Future<LicenseStatus> _fetchLicenseStatus() async {
    try {
      final token = await SecureStorageService.read('jwt_token');
      if (token == null || token.isEmpty) {
        return LicenseStatus.noToken;
      }

      final client = ApiClient();
      final response = await client.get('/auth/license/status');

      final data = response.data;
      if (data != null && data is Map<String, dynamic>) {
        return LicenseStatus.fromJson(data);
      }
      return LicenseStatus.unknown;
    } catch (e) {
      // On error, fail open - don't block users on network errors
      return LicenseStatus.unknown;
    }
  }

  /// Refresh the license status from the backend.
  Future<void> refresh() async {
    state = AsyncData(await _fetchLicenseStatus());
  }
}

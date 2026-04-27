// SAAS-019: Unit tests for LicenseStatus model
// Tests: fromJson, isExpiringSoon, isExpired, isGuest, remainingText

import 'package:flutter_test/flutter_test.dart';
import 'package:g777_client/features/auth/providers/license_status_provider.dart';

void main() {
  group('LicenseStatus', () {
    // ---------------------------------------------------------------
    // fromJson factory
    // ---------------------------------------------------------------
    group('fromJson', () {
      test('parses valid active license response', () {
        final json = {
          'is_valid': true,
          'reason': 'license_active',
          'role': 'user',
          'expires_at': '2026-05-26T00:00:00',
          'days_remaining': 30,
          'days_expired': null,
        };

        final status = LicenseStatus.fromJson(json);

        expect(status.isValid, true);
        expect(status.reason, 'license_active');
        expect(status.role, 'user');
        expect(status.expiresAt, '2026-05-26T00:00:00');
        expect(status.daysRemaining, 30);
        expect(status.daysExpired, isNull);
      });

      test('parses expired license response', () {
        final json = {
          'is_valid': false,
          'reason': 'license_expired',
          'role': 'user',
          'expires_at': '2026-04-20T00:00:00',
          'days_remaining': 0,
          'days_expired': 6,
        };

        final status = LicenseStatus.fromJson(json);

        expect(status.isValid, false);
        expect(status.reason, 'license_expired');
        expect(status.daysExpired, 6);
      });

      test('parses guest access response', () {
        final json = {
          'is_valid': true,
          'reason': 'guest_access',
          'role': 'guest',
          'expires_at': null,
          'days_remaining': null,
        };

        final status = LicenseStatus.fromJson(json);

        expect(status.isValid, true);
        expect(status.role, 'guest');
        expect(status.expiresAt, isNull);
        expect(status.daysRemaining, isNull);
      });

      test('handles missing fields with defaults', () {
        final json = <String, dynamic>{};

        final status = LicenseStatus.fromJson(json);

        expect(status.isValid, true); // default
        expect(status.reason, 'unknown'); // default
        expect(status.role, isNull);
        expect(status.daysRemaining, isNull);
      });
    });

    // ---------------------------------------------------------------
    // isExpiringSoon computed property
    // ---------------------------------------------------------------
    group('isExpiringSoon', () {
      test('returns true when daysRemaining is 7', () {
        const status = LicenseStatus(
          isValid: true,
          reason: 'license_active',
          daysRemaining: 7,
        );
        expect(status.isExpiringSoon, true);
      });

      test('returns true when daysRemaining is 0', () {
        const status = LicenseStatus(
          isValid: true,
          reason: 'license_active',
          daysRemaining: 0,
        );
        expect(status.isExpiringSoon, true);
      });

      test('returns true when daysRemaining is 1', () {
        const status = LicenseStatus(
          isValid: true,
          reason: 'license_active',
          daysRemaining: 1,
        );
        expect(status.isExpiringSoon, true);
      });

      test('returns false when daysRemaining is 8', () {
        const status = LicenseStatus(
          isValid: true,
          reason: 'license_active',
          daysRemaining: 8,
        );
        expect(status.isExpiringSoon, false);
      });

      test('returns false when daysRemaining is 30', () {
        const status = LicenseStatus(
          isValid: true,
          reason: 'license_active',
          daysRemaining: 30,
        );
        expect(status.isExpiringSoon, false);
      });

      test('returns false when daysRemaining is null', () {
        const status = LicenseStatus(isValid: true, reason: 'license_active');
        expect(status.isExpiringSoon, false);
      });

      test('returns false when daysRemaining is negative', () {
        const status = LicenseStatus(
          isValid: false,
          reason: 'license_expired',
          daysRemaining: -5,
        );
        expect(status.isExpiringSoon, false);
      });
    });

    // ---------------------------------------------------------------
    // isExpired computed property
    // ---------------------------------------------------------------
    group('isExpired', () {
      test('returns true when isValid is false', () {
        const status = LicenseStatus(isValid: false, reason: 'license_expired');
        expect(status.isExpired, true);
      });

      test('returns true when license is deactivated', () {
        const status = LicenseStatus(
          isValid: false,
          reason: 'license_deactivated',
        );
        expect(status.isExpired, true);
      });

      test('returns false when isValid is true', () {
        const status = LicenseStatus(isValid: true, reason: 'license_active');
        expect(status.isExpired, false);
      });
    });

    // ---------------------------------------------------------------
    // isGuest computed property
    // ---------------------------------------------------------------
    group('isGuest', () {
      test('returns true when role is guest', () {
        const status = LicenseStatus(
          isValid: true,
          reason: 'guest_access',
          role: 'guest',
        );
        expect(status.isGuest, true);
      });

      test('returns false when role is user', () {
        const status = LicenseStatus(
          isValid: true,
          reason: 'license_active',
          role: 'user',
        );
        expect(status.isGuest, false);
      });

      test('returns false when role is null', () {
        const status = LicenseStatus(isValid: true, reason: 'license_active');
        expect(status.isGuest, false);
      });
    });

    // ---------------------------------------------------------------
    // remainingText computed property
    // ---------------------------------------------------------------
    group('remainingText', () {
      test('returns "EXPIRED" when daysRemaining is 0', () {
        const status = LicenseStatus(
          isValid: false,
          reason: 'license_expired',
          daysRemaining: 0,
        );
        expect(status.remainingText, 'EXPIRED');
      });

      test('returns "EXPIRED" when daysRemaining is negative', () {
        const status = LicenseStatus(
          isValid: false,
          reason: 'license_expired',
          daysRemaining: -3,
        );
        expect(status.remainingText, 'EXPIRED');
      });

      test('returns "1 day" when daysRemaining is 1', () {
        const status = LicenseStatus(
          isValid: true,
          reason: 'license_active',
          daysRemaining: 1,
        );
        expect(status.remainingText, '1 day');
      });

      test('returns "5 days" when daysRemaining is 5', () {
        const status = LicenseStatus(
          isValid: true,
          reason: 'license_active',
          daysRemaining: 5,
        );
        expect(status.remainingText, '5 days');
      });

      test('returns "7 days" when daysRemaining is 7', () {
        const status = LicenseStatus(
          isValid: true,
          reason: 'license_active',
          daysRemaining: 7,
        );
        expect(status.remainingText, '7 days');
      });

      test('returns empty string when daysRemaining is null', () {
        const status = LicenseStatus(isValid: true, reason: 'guest_access');
        expect(status.remainingText, '');
      });
    });

    // ---------------------------------------------------------------
    // Static constants
    // ---------------------------------------------------------------
    group('static constants', () {
      test('unknown has isValid=true and reason=unknown', () {
        expect(LicenseStatus.unknown.isValid, true);
        expect(LicenseStatus.unknown.reason, 'unknown');
        expect(LicenseStatus.unknown.isGuest, false);
        expect(LicenseStatus.unknown.isExpired, false);
      });

      test('noToken has isValid=true, reason=no_token, role=guest', () {
        expect(LicenseStatus.noToken.isValid, true);
        expect(LicenseStatus.noToken.reason, 'no_token');
        expect(LicenseStatus.noToken.role, 'guest');
        expect(LicenseStatus.noToken.isGuest, true);
      });
    });
  });
}

// SAAS-019: Widget tests for LicenseExpiryBanner
// Tests: hidden state, warning banner, expired banner, force redirect

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import 'package:g777_client/features/auth/providers/license_status_provider.dart';
import 'package:g777_client/shared/widgets/license_expiry_banner.dart';

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

/// Creates a GoRouter with dashboard + login routes for redirect assertions.
GoRouter _createTestRouter() {
  return GoRouter(
    initialLocation: '/dashboard',
    routes: [
      GoRoute(
        path: '/dashboard',
        builder: (context, state) => const _TestDashboardScaffold(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const Scaffold(key: Key('login_page')),
      ),
    ],
  );
}

/// Host widget that places the banner inside a Column.
class _TestDashboardScaffold extends StatelessWidget {
  const _TestDashboardScaffold();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: const [
          LicenseExpiryBanner(),
          Expanded(child: Text('Dashboard content')),
        ],
      ),
    );
  }
}

/// Builds the full test widget tree with the given license state override.
/// Dart infers the correct `List<Override>` type from `overrideWith()`.
Widget _buildTestWidget(AsyncValue<LicenseStatus> licenseState) {
  return ProviderScope(
    overrides: [
      licenseStatusProvider.overrideWith(
        () => _FakeLicenseStatusNotifier(licenseState),
      ),
    ],
    child: MaterialApp.router(
      routerConfig: _createTestRouter(),
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.purple),
      ),
    ),
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  // ---------------------------------------------------------------
  // 1. Hidden states — banner should not render any visible content
  // ---------------------------------------------------------------
  group('LicenseExpiryBanner — hidden states', () {
    testWidgets('renders nothing for guest users', (tester) async {
      await tester.pumpWidget(
        _buildTestWidget(
          const AsyncData(
            LicenseStatus(isValid: true, reason: 'guest_access', role: 'guest'),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('SUBSCRIPTION EXPIRING SOON'), findsNothing);
      expect(find.text('LICENSE EXPIRED'), findsNothing);
    });

    testWidgets('renders nothing for unknown status', (tester) async {
      await tester.pumpWidget(
        _buildTestWidget(const AsyncData(LicenseStatus.unknown)),
      );
      await tester.pumpAndSettle();

      expect(find.text('SUBSCRIPTION EXPIRING SOON'), findsNothing);
      expect(find.text('LICENSE EXPIRED'), findsNothing);
    });

    testWidgets('renders nothing for no_token status', (tester) async {
      await tester.pumpWidget(
        _buildTestWidget(const AsyncData(LicenseStatus.noToken)),
      );
      await tester.pumpAndSettle();

      expect(find.text('SUBSCRIPTION EXPIRING SOON'), findsNothing);
      expect(find.text('LICENSE EXPIRED'), findsNothing);
    });

    testWidgets(
      'renders nothing when license is valid with >7 days remaining',
      (tester) async {
        await tester.pumpWidget(
          _buildTestWidget(
            const AsyncData(
              LicenseStatus(
                isValid: true,
                reason: 'license_active',
                role: 'user',
                daysRemaining: 30,
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('SUBSCRIPTION EXPIRING SOON'), findsNothing);
        expect(find.text('LICENSE EXPIRED'), findsNothing);
      },
    );

    testWidgets('renders nothing while loading', (tester) async {
      await tester.pumpWidget(
        _buildTestWidget(const AsyncLoading<LicenseStatus>()),
      );
      await tester.pump();

      expect(find.text('SUBSCRIPTION EXPIRING SOON'), findsNothing);
      expect(find.text('LICENSE EXPIRED'), findsNothing);
    });

    testWidgets('renders nothing on error', (tester) async {
      await tester.pumpWidget(
        _buildTestWidget(
          AsyncError<LicenseStatus>(Exception('test'), StackTrace.current),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('SUBSCRIPTION EXPIRING SOON'), findsNothing);
      expect(find.text('LICENSE EXPIRED'), findsNothing);
    });
  });

  // ---------------------------------------------------------------
  // 2. Warning banner — shows when ≤7 days remaining
  // ---------------------------------------------------------------
  group('LicenseExpiryBanner — warning state', () {
    testWidgets('shows "SUBSCRIPTION EXPIRING SOON" when 5 days remaining', (
      tester,
    ) async {
      await tester.pumpWidget(
        _buildTestWidget(
          const AsyncData(
            LicenseStatus(
              isValid: true,
              reason: 'license_active',
              role: 'user',
              daysRemaining: 5,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('SUBSCRIPTION EXPIRING SOON'), findsOneWidget);
      // "5 days" appears in both the description and the progress label
      expect(find.textContaining('5 days'), findsAtLeast(1));
      expect(find.text('RENEW'), findsOneWidget);
    });

    testWidgets(
      'shows "SUBSCRIPTION EXPIRING SOON" when exactly 7 days remaining',
      (tester) async {
        await tester.pumpWidget(
          _buildTestWidget(
            const AsyncData(
              LicenseStatus(
                isValid: true,
                reason: 'license_active',
                role: 'user',
                daysRemaining: 7,
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('SUBSCRIPTION EXPIRING SOON'), findsOneWidget);
        expect(find.textContaining('7 days'), findsAtLeast(1));
      },
    );

    testWidgets('shows "SUBSCRIPTION EXPIRING SOON" when 1 day remaining', (
      tester,
    ) async {
      await tester.pumpWidget(
        _buildTestWidget(
          const AsyncData(
            LicenseStatus(
              isValid: true,
              reason: 'license_active',
              role: 'user',
              daysRemaining: 1,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('SUBSCRIPTION EXPIRING SOON'), findsOneWidget);
      expect(find.textContaining('1 day'), findsAtLeast(1));
    });

    testWidgets('warning banner contains progress bar', (tester) async {
      await tester.pumpWidget(
        _buildTestWidget(
          const AsyncData(
            LicenseStatus(
              isValid: true,
              reason: 'license_active',
              role: 'user',
              daysRemaining: 3,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(LinearProgressIndicator), findsOneWidget);
    });

    testWidgets('warning banner shows URGENT label when ≤3 days', (
      tester,
    ) async {
      await tester.pumpWidget(
        _buildTestWidget(
          const AsyncData(
            LicenseStatus(
              isValid: true,
              reason: 'license_active',
              role: 'user',
              daysRemaining: 2,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('URGENT'), findsOneWidget);
    });
  });

  // ---------------------------------------------------------------
  // 3. Expired banner — shows when license is invalid
  // ---------------------------------------------------------------
  group('LicenseExpiryBanner — expired state', () {
    testWidgets('shows "LICENSE EXPIRED" when license is expired', (
      tester,
    ) async {
      await tester.pumpWidget(
        _buildTestWidget(
          const AsyncData(
            LicenseStatus(
              isValid: false,
              reason: 'license_expired',
              role: 'user',
              daysRemaining: 0,
              daysExpired: 5,
            ),
          ),
        ),
      );
      // Only pump once — pumpAndSettle would trigger the redirect to /login
      await tester.pump();

      expect(find.text('LICENSE EXPIRED'), findsOneWidget);
      expect(find.text('ACTIVATE'), findsOneWidget);
    });

    testWidgets(
      'shows deactivation message when reason is license_deactivated',
      (tester) async {
        await tester.pumpWidget(
          _buildTestWidget(
            const AsyncData(
              LicenseStatus(
                isValid: false,
                reason: 'license_deactivated',
                role: 'user',
                daysRemaining: 0,
              ),
            ),
          ),
        );
        // Only pump once — pumpAndSettle would trigger the redirect to /login
        await tester.pump();

        expect(find.text('LICENSE EXPIRED'), findsOneWidget);
        expect(find.textContaining('deactivated'), findsOneWidget);
      },
    );

    testWidgets('expired banner navigates to /login on next frame', (
      tester,
    ) async {
      await tester.pumpWidget(
        _buildTestWidget(
          const AsyncData(
            LicenseStatus(
              isValid: false,
              reason: 'license_expired',
              role: 'user',
              daysRemaining: 0,
            ),
          ),
        ),
      );
      // First pump renders the banner + schedules addPostFrameCallback
      await tester.pump();
      // Second pump processes the post-frame callback that calls context.go('/login')
      await tester.pumpAndSettle();

      // After redirect, the login page key should be present
      expect(find.byKey(const Key('login_page')), findsOneWidget);
    });
  });
}

// ---------------------------------------------------------------------------
// Fake notifier for overriding the provider in tests
// ---------------------------------------------------------------------------

class _FakeLicenseStatusNotifier extends LicenseStatusNotifier {
  final AsyncValue<LicenseStatus> _initialState;

  _FakeLicenseStatusNotifier(this._initialState);

  @override
  Future<LicenseStatus> build() async {
    state = _initialState;
    return _initialState.value!;
  }
}

import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../features/auth/presentation/pages/license_activation_page.dart';
import '../../features/dashboard/presentation/pages/dashboard_page.dart';
import '../../features/opportunity_hunter/presentation/pages/opportunity_hunter_page.dart';
import '../../features/settings/presentation/pages/settings_page.dart';

import '../../shared/layouts/main_layout.dart';

part 'app_router.g.dart';

@riverpod
GoRouter router(RouterRef ref) {
  // DEV MODE: No auth guards, all features unlocked for development.
  return GoRouter(
    initialLocation: '/dashboard',
    debugLogDiagnostics: false,
    routes: [
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LicenseActivationPage(),
      ),
      ShellRoute(
        builder: (context, state, child) {
          return MainLayout(child: child);
        },
        routes: [
          GoRoute(
            path: '/dashboard',
            name: 'dashboard',
            builder: (context, state) => const DashboardPage(),
          ),
          GoRoute(
            path: '/opportunity-hunter',
            name: 'opportunity-hunter',
            builder: (context, state) => const OpportunityHunterPage(),
          ),
          GoRoute(
            path: '/settings',
            name: 'settings',
            builder: (context, state) => const SettingsPage(),
          ),
        ],
      ),
    ],
  );
}

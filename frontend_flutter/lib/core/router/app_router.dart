import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../features/auth/presentation/pages/license_activation_page.dart';

import '../../features/dashboard/presentation/pages/dashboard_page.dart';
import '../../features/group_sender/presentation/pages/group_sender_page.dart';
import '../../features/members_grabber/presentation/pages/members_grabber_page.dart';
import '../../features/number_filter/presentation/pages/number_filter_page.dart';
import '../../features/opportunity_hunter/presentation/pages/opportunity_hunter_page.dart';
import '../../features/account_warmer/presentation/pages/account_warmer_page.dart';
import '../../features/poll_sender/presentation/pages/poll_sender_page.dart';
import '../../features/links_grabber/presentation/pages/links_grabber_page.dart';
import '../../features/theme_settings/presentation/pages/theme_settings_page.dart';
import '../../features/settings/presentation/pages/settings_page.dart';
import '../../features/crm/presentation/pages/crm_page.dart';

import '../../shared/layouts/main_layout.dart';

part 'app_router.g.dart';

@riverpod
GoRouter router(Ref ref) {
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
            path: '/group-sender',
            name: 'group-sender',
            builder: (context, state) => const GroupSenderPage(),
          ),
          GoRoute(
            path: '/members-grabber',
            name: 'members-grabber',
            builder: (context, state) => const MembersGrabberPage(),
          ),
          GoRoute(
            path: '/number-filter',
            name: 'number-filter',
            builder: (context, state) => const NumberFilterPage(),
          ),
          GoRoute(
            path: '/opportunity-hunter',
            name: 'opportunity-hunter',
            builder: (context, state) => const OpportunityHunterPage(),
          ),
          GoRoute(
            path: '/warmer',
            name: 'warmer',
            builder: (context, state) => const AccountWarmerPage(),
          ),
          GoRoute(
            path: '/crm',
            name: 'crm',
            builder: (context, state) => const CrmCustomersPage(),
          ),
          GoRoute(
            path: '/poll-sender',
            name: 'poll-sender',
            builder: (context, state) => const PollSenderPage(),
          ),
          GoRoute(
            path: '/links-grabber',
            name: 'links-grabber',
            builder: (context, state) => const LinksGrabberPage(),
          ),
          GoRoute(
            path: '/theme-settings',
            name: 'theme-settings',
            builder: (context, state) => const ThemeSettingsPage(),
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

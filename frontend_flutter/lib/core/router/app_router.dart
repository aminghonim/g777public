import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../shared/layouts/main_layout.dart';
import '../../features/dashboard/presentation/pages/dashboard_page.dart';
import '../../features/crm/presentation/pages/crm_page.dart';
import '../../features/settings/presentation/pages/settings_page.dart';

final GlobalKey<NavigatorState> _rootNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'root');
final GlobalKey<NavigatorState> _shellNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'shell');

final appRouter = GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: '/dashboard',
  routes: [
    ShellRoute(
      navigatorKey: _shellNavigatorKey,
      builder: (context, state, child) {
        return MainLayout(child: child);
      },
      routes: [
        GoRoute(
          path: '/dashboard',
          builder: (context, state) => const DashboardPage(),
        ),
        GoRoute(
          path: '/crm',
          builder: (context, state) => const CrmPage(),
        ),
        GoRoute(
          path: '/settings',
          builder: (context, state) => const SettingsPage(),
        ),
        // Placeholders for other routes mentioned in layout
        GoRoute(
          path: '/group-sender',
          builder: (context, state) => const Center(child: Text('Group Sender')),
        ),
        GoRoute(
          path: '/members-grabber',
          builder: (context, state) => const Center(child: Text('Members Grabber')),
        ),
        GoRoute(
          path: '/links-grabber',
          builder: (context, state) => const Center(child: Text('Links Grabber')),
        ),
        GoRoute(
          path: '/number-filter',
          builder: (context, state) => const Center(child: Text('Number Filter')),
        ),
        GoRoute(
          path: '/warmer',
          builder: (context, state) => const Center(child: Text('Warmer')),
        ),
        GoRoute(
          path: '/opportunity-hunter',
          builder: (context, state) => const Center(child: Text('Opp Hunter')),
        ),
      ],
    ),
  ],
);

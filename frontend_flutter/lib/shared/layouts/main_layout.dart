import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:g777_client/core/theme/theme.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'package:g777_client/shared/painters/custom_painters.dart';
import 'package:g777_client/shared/providers/locale_provider.dart';

class MainLayout extends ConsumerWidget {
  final Widget child;

  const MainLayout({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(localeProvider); // Trigger rebuild on locale change
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;
    final location = GoRouterState.of(context).uri.path;

    return SelectionArea(
      child: Scaffold(
        backgroundColor: colorScheme.surface,
        body: Stack(
          children: [
            if (isDark)
              CustomPaint(
                painter: CircuitBackgroundPainter(isDark: isDark),
                size: Size.infinite,
              ),
            Row(
              children: [
                _Sidebar(location: location),
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      border: Border(
                        left: BorderSide(
                          color: colorScheme.sidebarBorder,
                          width: 1,
                        ),
                      ),
                    ),
                    child: child,
                  ),
                ),
              ],
            ),
            Positioned(top: 20, right: 20, child: _TopControls()),
          ],
        ),
      ),
    );
  }
}

class _Sidebar extends ConsumerWidget {
  final String location;

  const _Sidebar({required this.location});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colorScheme = Theme.of(context).colorScheme;
    final l10n = AppLocalizations.of(context)!;

    return Container(
      width: 280,
      decoration: BoxDecoration(color: colorScheme.sidebarBackground),
      child: SingleChildScrollView(
        child: Column(
          children: [
            const SizedBox(height: 48),
            _buildLogo(colorScheme),
            const SizedBox(height: 60),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Wrap(
                spacing: 16,
                runSpacing: 24,
                alignment: WrapAlignment.center,
                children: [
                  _HexNavItem(
                    icon: Icons.dashboard_rounded,
                    label: l10n.dashboard,
                    accentColor: colorScheme.dashboardAccent,
                    route: '/dashboard',
                    isActive: location == '/dashboard',
                  ),
                  _HexNavItem(
                    icon: Icons.rocket_launch_rounded,
                    label: l10n.groupSender,
                    accentColor: colorScheme.groupSenderAccent,
                    route: '/group-sender',
                    isActive: location == '/group-sender',
                  ),
                  _HexNavItem(
                    icon: Icons.groups_rounded,
                    label: l10n.dataGrabber,
                    accentColor: colorScheme.membersAccent,
                    route: '/members-grabber',
                    isActive: location == '/members-grabber',
                  ),
                  _HexNavItem(
                    icon: Icons.link_rounded,
                    label: l10n.lblLinksGrabber,
                    accentColor: colorScheme.grabberAccent,
                    route: '/links-grabber',
                    isActive: location == '/links-grabber',
                  ),
                  _HexNavItem(
                    icon: Icons.filter_alt_rounded,
                    label: l10n.numberValidator,
                    accentColor: colorScheme.secondary,
                    route: '/number-filter',
                    isActive: location == '/number-filter',
                  ),
                  _HexNavItem(
                    icon: Icons.whatshot_rounded,
                    label: l10n.accountWarmer,
                    accentColor: colorScheme.statusWarning,
                    route: '/warmer',
                    isActive: location == '/warmer',
                  ),
                  _HexNavItem(
                    icon: Icons.travel_explore_rounded,
                    label: l10n.opportunityHunter,
                    accentColor: colorScheme.tertiary,
                    route: '/opportunity-hunter',
                    isActive: location == '/opportunity-hunter',
                  ),
                  _HexNavItem(
                    icon: Icons.settings_rounded,
                    label: l10n.settings,
                    accentColor: colorScheme.primary,
                    route: '/settings',
                    isActive: location == '/settings',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildLogo(ColorScheme colorScheme) {
    return Column(
      children: [
        Text(
          'G777',
          style: TextStyle(
            color: colorScheme.sidebarLogo,
            fontSize: 42,
            fontWeight: FontWeight.w900,
            letterSpacing: 4,
            fontFamily: 'Oxanium',
            shadows: [
              Shadow(
                color: colorScheme.sidebarLogo.withValues(alpha: 0.8),
                blurRadius: 15,
              ),
            ],
          ),
        ),
        Text(
          'ULTIMATE',
          style: TextStyle(
            color: colorScheme.onSurface.withValues(alpha: 0.4),
            fontSize: 14,
            letterSpacing: 8,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}

class _HexNavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color accentColor;
  final String route;
  final bool isActive;

  const _HexNavItem({
    required this.icon,
    required this.label,
    required this.accentColor,
    required this.route,
    required this.isActive,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final displayColor = isActive
        ? accentColor
        : colorScheme.onSurface.withValues(alpha: 0.4);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        GestureDetector(
          onTap: () => context.go(route),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            width: 80,
            height: 80,
            decoration: ShapeDecoration(
              shape: HexagonBorder(
                side: BorderSide(
                  color: isActive
                      ? accentColor
                      : colorScheme.outline.withValues(alpha: 0.2),
                  width: isActive ? 3 : 2,
                ),
                isActive: isActive,
              ),
              shadows: isActive
                  ? [
                      BoxShadow(
                        color: accentColor.withValues(alpha: 0.5),
                        blurRadius: 20,
                      ),
                    ]
                  : [],
            ),
            child: Center(child: Icon(icon, color: displayColor, size: 30)),
          ),
        ),
        const SizedBox(height: 8),
        SizedBox(
          width: 80,
          child: Text(
            label,
            style: TextStyle(
              color: isActive
                  ? colorScheme.onSurface
                  : colorScheme.onSurface.withValues(alpha: 0.5),
              fontSize: 10,
              fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
              fontFamily: 'Oxanium',
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}

class _TopControls extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        _CircleIconButton(icon: Icons.notifications_rounded, onTap: () {}),
      ],
    );
  }
}

class _CircleIconButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;

  const _CircleIconButton({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(30),
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainer.withValues(alpha: 0.5),
          shape: BoxShape.circle,
          border: Border.all(color: colorScheme.outline.withValues(alpha: 0.1)),
        ),
        child: Icon(icon, color: colorScheme.onSurface, size: 20),
      ),
    );
  }
}

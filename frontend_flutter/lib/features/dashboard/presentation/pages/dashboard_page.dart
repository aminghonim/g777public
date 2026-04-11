import 'package:g777_client/core/theme/theme.dart'; // Unified theme system
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'package:g777_client/shared/providers/locale_provider.dart';
import 'package:g777_client/shared/providers/theme_provider.dart';
import '../widgets/live_telemetry_widget.dart';
import '../widgets/whatsapp_status_card.dart';
import '../widgets/style_selector.dart';
import '../widgets/system_stats_grid.dart';
import '../widgets/campaign_stats_grid.dart';
import 'package:g777_client/shared/providers/logs_provider.dart';
import 'package:g777_client/features/group_sender/presentation/controllers/group_sender_controller.dart';
import 'package:g777_client/features/analytics/presentation/widgets/campaign_analytics_widget.dart';
import 'package:g777_client/features/evolution/presentation/widgets/instance_connection_widget.dart';
import 'package:g777_client/features/settings/presentation/widgets/quota_dashboard_widget.dart';

class DashboardPage extends ConsumerWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeController = ThemeController(ref);
    final currentStyle = ref.watch(themeStyleProvider);
    final themeMode = ref.watch(themeModeProvider);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = themeMode.flutterThemeMode == ThemeMode.dark;

    // Gap 2: Active bridges for singleton SSE pipeline
    ref.watch(logsStreamListenerProvider);
    ref.watch(campaignStreamListenerProvider);

    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      body: SelectionArea(
        child: Container(
          decoration: _buildBackgroundDecoration(isDark, currentStyle, theme),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(
                  context,
                  ref,
                  themeController,
                  themeMode.flutterThemeMode,
                  colorScheme,
                  l10n,
                ),
                const SizedBox(height: 32),

                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // LEFT COLUMN: MAIN STATUS
                    const Expanded(
                      flex: 2,
                      child: Column(
                        children: [
                          CampaignAnalyticsWidget(),
                          SizedBox(height: 24),
                          QuotaDashboardWidget(),
                          SizedBox(height: 24),
                          InstanceConnectionWidget(),
                          SizedBox(height: 24),
                          WhatsAppStatusCard(),
                          SizedBox(height: 24),
                          SystemStatsGrid(),
                          SizedBox(height: 24),
                          CampaignStatsGrid(),
                        ],
                      ),
                    ),
                    const SizedBox(width: 24),
                    // RIGHT COLUMN: TELEMETRY & STYLE
                    Expanded(
                      child: Column(
                        children: [
                          StyleSelector(
                            controller: themeController,
                            currentStyle: currentStyle,
                          ),
                          const SizedBox(height: 24),
                          const LiveTelemetryWidget(),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ), // closes Column
          ), // closes SingleChildScrollView
        ), // closes Container
      ), // closes SelectionArea
    );
  }

  Widget _buildHeader(
    BuildContext context,
    WidgetRef ref,
    ThemeController controller,
    ThemeMode mode,
    ColorScheme colorScheme,
    AppLocalizations l10n,
  ) {
    final locale = ref.watch(localeProvider);
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              FittedBox(
                fit: BoxFit.scaleDown,
                alignment: Alignment.centerLeft,
                child: Text(
                  l10n.appTitle.toUpperCase(),
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                    fontFamily: 'Oxanium',
                    color: colorScheme.dashboardAccent,
                    shadows: [
                      Shadow(
                        color: colorScheme.dashboardAccent,
                        blurRadius: 10,
                      ),
                    ],
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Text(
                l10n.orchestrationTerminal,
                style: TextStyle(
                  fontSize: 12,
                  color: colorScheme.onSurface.withValues(alpha: 0.4),
                  letterSpacing: 4,
                  fontWeight: FontWeight.bold,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Language Switcher
            TextButton.icon(
              onPressed: () => ref.read(localeProvider.notifier).toggleLocale(),
              icon: const Icon(Icons.language_rounded, size: 18),
              label: Text(locale.languageCode.toUpperCase()),
              style: TextButton.styleFrom(
                backgroundColor: colorScheme.surfaceContainer.withValues(
                  alpha: 0.5,
                ),
                foregroundColor: colorScheme.primary,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              onPressed: () => controller.toggleThemeMode(),
              icon: Icon(
                mode == ThemeMode.dark
                    ? Icons.light_mode_rounded
                    : Icons.dark_mode_rounded,
              ),
              style: IconButton.styleFrom(
                backgroundColor: colorScheme.surfaceContainer,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  BoxDecoration _buildBackgroundDecoration(
    bool isDark,
    ThemeStyle style,
    ThemeData theme,
  ) {
    final colorScheme = theme.colorScheme;
    if (!isDark) return BoxDecoration(color: theme.scaffoldBackgroundColor);

    return BoxDecoration(
      gradient: colorScheme.dashboardGradient.length > 1
          ? (style == ThemeStyle.neon || style == ThemeStyle.modernGlass
                ? RadialGradient(
                    center: style == ThemeStyle.neon
                        ? const Alignment(0, -0.5)
                        : Alignment.topLeft,
                    radius: style == ThemeStyle.neon ? 1.5 : 1.2,
                    colors: colorScheme.dashboardGradient,
                  )
                : LinearGradient(
                    begin: style == ThemeStyle.professional
                        ? Alignment.topLeft
                        : Alignment.topCenter,
                    end: style == ThemeStyle.professional
                        ? Alignment.bottomRight
                        : Alignment.bottomCenter,
                    colors: colorScheme.dashboardGradient,
                  ))
          : null,
      color: colorScheme.dashboardGradient.length == 1
          ? colorScheme.dashboardGradient.first
          : null,
    );
  }
}

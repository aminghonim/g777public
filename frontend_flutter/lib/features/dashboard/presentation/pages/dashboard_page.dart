import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/theme_controller.dart';
import '../../../../shared/providers/theme_provider.dart';
import '../../../../shared/providers/locale_provider.dart';
import '../../../../l10n/app_localizations.dart';
import '../../../../core/theme/semantic_colors.dart';
import '../widgets/live_telemetry_widget.dart';
import '../widgets/whatsapp_status_card.dart';
import '../widgets/style_selector.dart';
import '../widgets/system_stats_grid.dart';
import '../widgets/campaign_stats_grid.dart';
import '../../../../shared/providers/logs_provider.dart';
import '../../../analytics/presentation/widgets/campaign_analytics_widget.dart';
import '../../../evolution/presentation/widgets/instance_connection_widget.dart';
import '../../../settings/presentation/widgets/quota_dashboard_widget.dart';

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

    // Bridge listeners
    ref.watch(logsStreamListenerProvider);

    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: SelectionArea(
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
          ),
        ),
      ),
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
              Text(
                l10n.appTitle.toUpperCase(),
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                  fontFamily: 'Oxanium',
                  color: colorScheme.sidebarLogo,
                  shadows: [
                    Shadow(color: colorScheme.sidebarLogo, blurRadius: 10),
                  ],
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
              ),
            ],
          ),
        ),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextButton.icon(
              onPressed: () => ref.read(localeProvider.notifier).toggleLocale(),
              icon: const Icon(Icons.language_rounded, size: 18),
              label: Text(locale.languageCode.toUpperCase()),
              style: TextButton.styleFrom(
                backgroundColor: colorScheme.surfaceContainer.withValues(alpha: 0.5),
                foregroundColor: colorScheme.primary,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              onPressed: () => controller.toggleThemeMode(),
              icon: Icon(
                mode == ThemeMode.dark ? Icons.light_mode_rounded : Icons.dark_mode_rounded,
              ),
              style: IconButton.styleFrom(
                backgroundColor: colorScheme.surfaceContainer,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

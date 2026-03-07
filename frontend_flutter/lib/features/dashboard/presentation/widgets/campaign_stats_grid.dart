import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'package:g777_client/core/theme/theme.dart'; // Unified theme system

class CampaignStatsGrid extends ConsumerWidget {
  const CampaignStatsGrid({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;

    // For now using dummy data, later connect to a provider
    const stats = {'sent': 1240, 'failed': 12, 'pending': 450};

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 16),
          child: Text(
            l10n.campaigns.toUpperCase(),
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
              color: colors.onSurface.withValues(alpha: 0.5),
            ),
          ),
        ),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 3,
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          childAspectRatio: 1.2,
          children: [
            _buildStatCard(
              context,
              l10n.sent,
              stats['sent'].toString(),
              Icons.send_rounded,
              colors.sendSuccess,
            ),
            _buildStatCard(
              context,
              l10n.failed,
              stats['failed'].toString(),
              Icons.error_outline_rounded,
              colors.sendError,
            ),
            _buildStatCard(
              context,
              l10n.pending,
              stats['pending'].toString(),
              Icons.pending_actions_rounded,
              colors.sendProgress,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatCard(
    BuildContext context,
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark
            ? color.withValues(alpha: 0.05)
            : color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: isDark ? 0.2 : 0.4)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 18, color: color),
          const SizedBox(height: 12),
          FittedBox(
            fit: BoxFit.scaleDown,
            child: SelectableText(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.w900,
                color: isDark ? color : Color.lerp(color, Colors.black, 0.2),
                fontFamily: 'monospace',
              ),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label.toUpperCase(),
            style: TextStyle(
              fontSize: 9,
              fontWeight: FontWeight.bold,
              color: colors(context).onSurface.withValues(alpha: 0.5),
              letterSpacing: 1,
            ),
          ),
        ],
      ),
    );
  }

  // Helper to get color scheme from context since we are in a helper method
  ColorScheme colors(BuildContext context) => Theme.of(context).colorScheme;
}

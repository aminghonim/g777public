import 'package:flutter/material.dart';
import '../../../../core/theme/semantic_colors.dart';
import '../../../../l10n/app_localizations.dart';

class CampaignAnalyticsWidget extends StatelessWidget {
  const CampaignAnalyticsWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final l10n = AppLocalizations.of(context)!;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: colorScheme.outline.withValues(alpha: 0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'ANALYTICS VELOCITY',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w900,
              letterSpacing: 2,
              color: colorScheme.dashboardAccent,
            ),
          ),
          const SizedBox(height: 24),
          Container(
            height: 120,
            width: double.infinity,
            decoration: BoxDecoration(
              color: colorScheme.surface.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: colorScheme.outline.withValues(alpha: 0.05)),
            ),
            child: const Center(
              child: Icon(Icons.show_chart_rounded, size: 64, color: Colors.cyanAccent),
            ),
          ),
        ],
      ),
    );
  }
}

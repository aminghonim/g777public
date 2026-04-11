import 'package:flutter/material.dart';
import '../../../../core/theme/semantic_colors.dart';
import '../../../../l10n/app_localizations.dart';

class CampaignStatsGrid extends StatelessWidget {
  const CampaignStatsGrid({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final l10n = AppLocalizations.of(context)!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.campaigns.toUpperCase(),
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w900,
            letterSpacing: 2,
            color: colorScheme.onSurface.withValues(alpha: 0.5),
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(child: _buildSimpleStat(l10n.sent, '4,281', colorScheme.statusOnline)),
            const SizedBox(width: 12),
            Expanded(child: _buildSimpleStat(l10n.failed, '24', colorScheme.statusError)),
            const SizedBox(width: 12),
            Expanded(child: _buildSimpleStat(l10n.pending, '156', colorScheme.statusWarning)),
          ],
        ),
      ],
    );
  }

  Widget _buildSimpleStat(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Column(
        children: [
          Text(
            label.toUpperCase(),
            style: TextStyle(
              fontSize: 9,
              fontWeight: FontWeight.bold,
              color: color.withValues(alpha: 0.6),
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w900,
              color: color,
              fontFamily: 'monospace',
            ),
          ),
        ],
      ),
    );
  }
}

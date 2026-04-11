import 'package:flutter/material.dart';
import '../../../../core/theme/semantic_colors.dart';
import '../../../../l10n/app_localizations.dart';

class LiveTelemetryWidget extends StatelessWidget {
  const LiveTelemetryWidget({super.key});

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
            l10n.liveTelemetry.toUpperCase(),
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w900,
              letterSpacing: 2,
              color: colorScheme.primary,
            ),
          ),
          const SizedBox(height: 24),
          _buildMetricRow(context, 'API LATENCY', '142ms', colorScheme.statusOnline),
          const SizedBox(height: 16),
          _buildMetricRow(context, 'THROUGHPUT', '4.2 req/s', colorScheme.statusInfo),
          const SizedBox(height: 16),
          _buildMetricRow(context, 'CPU LOAD', '12%', colorScheme.statusOnline),
          const SizedBox(height: 16),
          _buildMetricRow(context, 'MEMORY', '256MB', colorScheme.statusWarning),
        ],
      ),
    );
  }

  Widget _buildMetricRow(BuildContext context, String label, String value, Color color) {
    final colorScheme = Theme.of(context).colorScheme;
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.bold,
            color: colorScheme.onSurface.withValues(alpha: 0.4),
            letterSpacing: 1,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w900,
            fontFamily: 'monospace',
            color: color,
          ),
        ),
      ],
    );
  }
}

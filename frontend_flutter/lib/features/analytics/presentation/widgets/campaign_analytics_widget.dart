import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/analytics_provider.dart';
import '../../../../core/theme/theme_extensions.dart';
import 'package:g777_client/core/theme/semantic_colors.dart';

import 'package:g777_client/features/analytics/data/models/analytics_model.dart';

class CampaignAnalyticsWidget extends ConsumerWidget {
  const CampaignAnalyticsWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final analyticsAsync = ref.watch(analyticsProvider);
    final theme = Theme.of(context);
    final ext = theme.extension<G777ThemeExtension>();

    return analyticsAsync.when(
      data: (data) => _buildBody(context, data, ext),
      loading: () => _buildLoading(context),
      error: (err, stack) => _buildError(context, err.toString()),
    );
  }

  Widget _buildBody(
    BuildContext context,
    AnalyticsModel data,
    G777ThemeExtension? ext,
  ) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final blur = ext?.glassBlur ?? 0.0;
    final opacity = ext?.glassOpacity ?? 1.0;
    final glow = ext?.glowColor;
    final radius = ext?.edgeRadius ?? 24.0;

    Widget content = Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colors.surface.withValues(alpha: 0.05 * opacity),
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(
          color: colors.onSurface.withValues(alpha: 0.1),
          width: 1,
        ),
        boxShadow: glow != null
            ? [
                BoxShadow(
                  color: glow.withValues(alpha: 0.15),
                  blurRadius: ext?.glowIntensity ?? 10.0,
                  spreadRadius: 2,
                ),
              ]
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: colors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  Icons.analytics_rounded,
                  color: colors.primary,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                'CAMPAIGN INTELLIGENCE',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 2,
                  fontFamily: 'Oxanium',
                ),
              ),
              const Spacer(),
              IconButton(
                onPressed: () {}, // Refresh logic if needed
                icon: Icon(
                  Icons.more_vert_rounded,
                  color: colors.onSurface.withValues(alpha: 0.4),
                ),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
              ),
            ],
          ),
          const SizedBox(height: 32),
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            childAspectRatio: 1.8,
            children: [
              _buildMetricCard(
                context,
                'Total Sent',
                data.totalMessagesSent.toString(),
                Icons.auto_graph_rounded,
                colors.primary,
              ),
              _buildMetricCard(
                context,
                'Remaining',
                data.dailyRemaining.toString(),
                Icons.hourglass_bottom_rounded,
                colors.statusOnline,
              ),
              _buildMetricCard(
                context,
                'Daily Limit',
                data.dailyLimit.toString(),
                Icons.speed_rounded,
                colors.statusWarning,
              ),
              _buildMetricCard(
                context,
                'Active Instances',
                '${data.activeInstances} / ${data.maxInstances}',
                Icons.dns_rounded,
                colors.telemetryPrimary,
              ),
            ],
          ),
        ],
      ),
    );

    if (blur > 0) {
      content = ClipRRect(
        borderRadius: BorderRadius.circular(radius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
          child: content,
        ),
      );
    }

    return content;
  }

  Widget _buildMetricCard(
    BuildContext context,
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    final theme = Theme.of(context);
    final ext = theme.extension<G777ThemeExtension>();
    final radius = ext?.edgeRadius ?? 20.0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(color: color.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 14, color: color),
              const SizedBox(width: 8),
              Text(
                label.toUpperCase(),
                style: TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
                ),
              ),
            ],
          ),
          const Spacer(),
          Text(
            value,
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w900,
              fontFamily: 'monospace',
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoading(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Container(
      height: 200,
      decoration: BoxDecoration(
        color: colors.onSurface.withValues(alpha: 0.02),
        borderRadius: BorderRadius.circular(24),
      ),
      child: const Center(child: CircularProgressIndicator()),
    );
  }

  Widget _buildError(BuildContext context, String error) {
    final colors = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colors.statusError.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: colors.statusError.withValues(alpha: 0.2)),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline_rounded, color: colors.statusError),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              error,
              style: TextStyle(color: colors.statusError, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }
}

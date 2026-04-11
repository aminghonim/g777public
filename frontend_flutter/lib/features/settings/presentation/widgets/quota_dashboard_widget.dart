import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/theme_extensions.dart';
import '../providers/quota_provider.dart';
import 'package:g777_client/core/theme/semantic_colors.dart';

class QuotaDashboardWidget extends ConsumerWidget {
  const QuotaDashboardWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final quotaAsync = ref.watch(quotaProvider);
    final theme = Theme.of(context);
    final ext = theme.extension<G777ThemeExtension>();

    return quotaAsync.when(
      data: (data) {
        final double messageCount = (data['message_count'] ?? 0).toDouble();
        final double dailyLimit = (data['daily_limit'] ?? 1000).toDouble();
        final double instanceCount = (data['instance_count'] ?? 0).toDouble();
        final double maxInstances = (data['max_instances'] ?? 1).toDouble();

        final messageProgress = dailyLimit > 0
            ? messageCount / dailyLimit
            : 0.0;
        final instanceProgress = maxInstances > 0
            ? instanceCount / maxInstances
            : 0.0;

        return _buildGlassCard(
          context,
          ext,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.speed_rounded,
                    color: theme.colorScheme.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'QUOTA & USAGE',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w900,
                      fontFamily: 'Oxanium',
                      letterSpacing: 1.5,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              _buildProgressRow(
                context,
                'Daily Messages',
                messageCount.toInt(),
                dailyLimit.toInt(),
                messageProgress,
                theme.colorScheme.primary,
              ),
              const SizedBox(height: 24),
              _buildProgressRow(
                context,
                'WhatsApp Instances',
                instanceCount.toInt(),
                maxInstances.toInt(),
                instanceProgress,
                theme.colorScheme.secondary,
              ),
              const SizedBox(height: 32),
              Center(
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      if (ext?.glowColor != null)
                        BoxShadow(
                          color: ext!.glowColor!.withValues(alpha: 0.3),
                          blurRadius: 15,
                          spreadRadius: -2,
                        ),
                    ],
                  ),
                  child: ElevatedButton.icon(
                    onPressed: () {
                      _showUpgradeDialog(context);
                    },
                    icon: const Icon(Icons.upgrade_rounded, size: 20),
                    label: const Text(
                      'UPGRADE TO PRO',
                      style: TextStyle(
                        fontFamily: 'Oxanium',
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 40,
                        vertical: 16,
                      ),
                      backgroundColor: theme.colorScheme.primary,
                      foregroundColor: theme.colorScheme.onPrimary,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                        side: BorderSide(
                          color: theme.colorScheme.onPrimary.withValues(
                            alpha: 0.2,
                          ),
                          width: 1,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
      loading: () => const _LoadingPlaceholder(),
      error: (err, _) => _ErrorPlaceholder(error: err.toString()),
    );
  }

  void _showUpgradeDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Theme.of(context).colorScheme.surface,
        title: const Text('Upgrade Tier'),
        content: const Text(
          'To unlock higher messaging limits and more instances, please contact the administration or visit the billing portal.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('CLOSE'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('PORTAL'),
          ),
        ],
      ),
    );
  }

  Widget _buildGlassCard(
    BuildContext context,
    G777ThemeExtension? ext, {
    required Widget child,
  }) {
    final colorScheme = Theme.of(context).colorScheme;
    final blur = ext?.glassBlur ?? 0.0;
    final opacity = ext?.glassOpacity ?? 1.0;
    final glow = ext?.glowColor;
    final radius = ext?.edgeRadius ?? 20.0;

    Widget content = Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colorScheme.surface.withValues(alpha: 0.05 * opacity),
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(
          color: colorScheme.onSurface.withValues(alpha: 0.1),
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
      child: child,
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

  Widget _buildProgressRow(
    BuildContext context,
    String label,
    int current,
    int limit,
    double progress,
    Color color,
  ) {
    final theme = Theme.of(context);
    final isCritical = progress >= 0.9;
    final displayColor = isCritical ? theme.colorScheme.statusError : color;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label.toUpperCase(),
              style: theme.textTheme.labelLarge?.copyWith(
                letterSpacing: 1.2,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
              ),
            ),
            Text(
              '$current / $limit',
              style: theme.textTheme.bodyMedium?.copyWith(
                fontFamily: 'monospace',
                fontWeight: FontWeight.bold,
                color: isCritical
                    ? theme.colorScheme.statusError
                    : theme.colorScheme.onSurface,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Stack(
          children: [
            Container(
              height: 10,
              decoration: BoxDecoration(
                color: displayColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(5),
              ),
            ),
            FractionallySizedBox(
              widthFactor: progress.clamp(0.0, 1.0),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 800),
                curve: Curves.easeOutCubic,
                height: 10,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [displayColor, displayColor.withValues(alpha: 0.7)],
                  ),
                  borderRadius: BorderRadius.circular(5),
                  boxShadow: [
                    BoxShadow(
                      color: displayColor.withValues(alpha: 0.3),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _LoadingPlaceholder extends StatelessWidget {
  const _LoadingPlaceholder();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 200,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(20),
      ),
      child: const Center(child: CircularProgressIndicator()),
    );
  }
}

class _ErrorPlaceholder extends StatelessWidget {
  final String error;
  const _ErrorPlaceholder({required this.error});

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colors.statusError.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: colors.statusError.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Icon(Icons.error_outline_rounded, color: colors.statusError),
          const SizedBox(height: 8),
          Text(
            error,
            style: TextStyle(color: colors.statusError, fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

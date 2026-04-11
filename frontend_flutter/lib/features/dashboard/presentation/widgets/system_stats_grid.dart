import 'package:flutter/material.dart';
import '../../../../core/theme/theme_extensions.dart';
import '../../../../shared/painters/custom_painters.dart';
import 'dart:ui';
import '../../../../core/theme/semantic_colors.dart';
import '../../../../l10n/app_localizations.dart';

class SystemStatsGrid extends StatelessWidget {
  const SystemStatsGrid({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;

    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 16,
      crossAxisSpacing: 16,
      childAspectRatio: 1.6,
      children: [
        _buildStatTile(
          context,
          l10n.secureStorage,
          l10n.ready,
          Icons.lock,
          colorScheme.navAdvancedSender,
        ),
        _buildStatTile(
          context,
          l10n.portDiscovery,
          l10n.standby,
          Icons.router,
          colorScheme.navUtilities,
        ),
        _buildStatTile(
          context,
          l10n.aiCore,
          l10n.active,
          Icons.psychology,
          colorScheme.navGroupTools,
        ),
        _buildStatTile(
          context,
          l10n.telemetry,
          l10n.live,
          Icons.radar,
          colorScheme.styleNeon,
        ),
      ],
    );
  }

  Widget _buildStatTile(
    BuildContext context,
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final extension = theme.extension<G777ThemeExtension>();

    final double blur = extension?.glassBlur ?? 0.0;
    final double opacity = extension?.glassOpacity ?? 1.0;
    final double corner = extension?.edgeRadius ?? 16.0;
    final double bevel = extension?.cutCornerSize ?? 0.0;

    Widget content = Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: isDark
            ? color.withValues(alpha: 0.03 * opacity)
            : color.withValues(alpha: 0.1 * opacity),
        borderRadius: bevel > 0 ? null : BorderRadius.circular(corner),
        border: bevel > 0
            ? null
            : Border.all(color: color.withValues(alpha: isDark ? 0.15 : 0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Row(
            children: [
              Icon(
                icon,
                size: 14,
                color: color.withValues(alpha: isDark ? 0.5 : 0.8),
              ),
              const SizedBox(width: 8),
              Flexible(
                child: FittedBox(
                  fit: BoxFit.scaleDown,
                  child: Text(
                    label,
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.bold,
                      color: color.withValues(alpha: isDark ? 0.5 : 0.8),
                      letterSpacing: 1,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              value,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w900,
                color: isDark
                    ? color
                    : Color.lerp(color, theme.colorScheme.onSurface, 0.3),
                fontFamily: 'monospace',
              ),
            ),
          ),
        ],
      ),
    );

    if (bevel > 0) {
      content = Container(
        decoration: ShapeDecoration(
          color: isDark
              ? color.withValues(alpha: 0.03 * opacity)
              : color.withValues(alpha: 0.1 * opacity),
          shape: AppBeveledRectangleBorder(
            side: BorderSide(
              color: color.withValues(alpha: isDark ? 0.15 : 0.4),
              width: 1,
            ),
            bevelSize: bevel,
            borderRadius: BorderRadius.circular(corner),
          ),
        ),
        child: content,
      );
    }

    if (blur > 0) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(corner),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
          child: content,
        ),
      );
    }

    return content;
  }
}

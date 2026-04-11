import 'package:flutter/material.dart';
import '../../../../core/theme/theme_extensions.dart';
import '../../../../core/theme/semantic_colors.dart';
import '../../../../l10n/app_localizations.dart';

class WhatsAppStatusCard extends StatelessWidget {
  const WhatsAppStatusCard({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;
    final extension = theme.extension<G777ThemeExtension>();

    // Mock data for initial materialization
    const bool isConnected = true;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(extension?.edgeRadius ?? 20),
        border: Border.all(color: colorScheme.outline.withValues(alpha: 0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l10n.whatsappStatus.toUpperCase(),
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 2,
                  color: colorScheme.onSurface.withValues(alpha: 0.5),
                ),
              ),
              _buildStatusIndicator(isConnected, colorScheme, l10n),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Icon(
                isConnected ? Icons.check_circle_rounded : Icons.error_outline_rounded,
                size: 48,
                color: isConnected ? colorScheme.statusOnline : colorScheme.statusError,
              ),
              const SizedBox(width: 20),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isConnected ? l10n.whatsappLinked : l10n.whatsappDisconnected,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      fontFamily: 'Oxanium',
                    ),
                  ),
                  Text(
                    'SESSION: GLOBAL_NODE_01',
                    style: TextStyle(
                      fontSize: 11,
                      color: colorScheme.onSurface.withValues(alpha: 0.4),
                      letterSpacing: 2,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatusIndicator(bool connected, ColorScheme colors, AppLocalizations l10n) {
    final color = connected ? colors.statusOnline : colors.statusError;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(color: color.withValues(alpha: 0.5), blurRadius: 6),
              ],
            ),
          ),
          const SizedBox(width: 6),
          Text(
            (connected ? l10n.online : 'OFFLINE').toUpperCase(),
            style: TextStyle(
              fontSize: 9,
              fontWeight: FontWeight.w900,
              color: color,
              letterSpacing: 1,
            ),
          ),
        ],
      ),
    );
  }
}

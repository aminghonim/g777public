import 'package:g777_client/shared/painters/custom_painters.dart';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/shared/providers/wa_status_provider.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'pairing_dialog.dart';
import 'package:g777_client/core/theme/theme.dart'; // Unified theme system

class WhatsAppStatusCard extends ConsumerWidget {
  const WhatsAppStatusCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = ref.watch(waStatusProvider);
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;
    final l10n = AppLocalizations.of(context)!;
    final extension = theme.extension<G777ThemeExtension>();

    final double blur = extension?.glassBlur ?? 0.0;
    final double opacity = extension?.glassOpacity ?? 1.0;
    final double corner = extension?.edgeRadius ?? 24.0;
    final double bevel = extension?.cutCornerSize ?? 0.0;
    final double glowIntensity = extension?.glowIntensity ?? 20.0;

    final accent = status.isConnected
        ? colors.telemetryGreen
        : colors.statusError;

    Widget cardContent = Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: accent.withValues(alpha: (isDark ? 0.05 : 0.1) * opacity),
        borderRadius: bevel > 0 ? null : BorderRadius.circular(corner),
        border: bevel > 0
            ? null
            : Border.all(
                color: accent.withValues(alpha: isDark ? 0.2 : 0.4),
                width: 2,
              ),
        boxShadow: glowIntensity > 0
            ? [
                BoxShadow(
                  color: accent.withValues(alpha: isDark ? 0.05 : 0.1),
                  blurRadius: glowIntensity,
                  spreadRadius: 0,
                ),
              ]
            : null,
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: accent.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                  border: Border.all(color: accent.withValues(alpha: 0.3)),
                ),
                child: Icon(
                  status.isConnected
                      ? Icons.check_circle_rounded
                      : Icons.warning_rounded,
                  color: accent,
                  size: 32,
                ),
              ),
              const SizedBox(width: 24),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    FittedBox(
                      fit: BoxFit.scaleDown,
                      alignment: Alignment.centerLeft,
                      child: Text(
                        status.isConnected
                            ? l10n.whatsappLinked
                            : l10n.whatsappDisconnected,
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.w900,
                          color: accent,
                          fontFamily: 'Oxanium',
                        ),
                      ),
                    ),
                    SelectableText(
                      status.isConnected
                          ? '${l10n.instance}: ${status.details?['instance']?['name'] ?? 'G777'} | ${l10n.status}: ${l10n.online}'
                          : l10n.systemStandby,
                      style: TextStyle(
                        color: colors.onSurface.withValues(alpha: 0.5),
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 2,
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: () =>
                    ref.read(waStatusProvider.notifier).refreshStatus(),
                icon: const Icon(Icons.refresh_rounded, size: 20),
                style: IconButton.styleFrom(
                  backgroundColor: accent.withValues(alpha: 0.1),
                  foregroundColor: accent,
                ),
              ),
            ],
          ),
          const SizedBox(height: 32),
          Row(
            children: [
              if (!status.isConnected)
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      _showPairingDialog(context, ref);
                    },
                    icon: const Icon(Icons.hub_rounded),
                    label: Text(l10n.initializePairing),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: accent,
                      foregroundColor: isDark ? Colors.black : Colors.white,
                      minimumSize: const Size(0, 56),
                      shape: bevel > 0
                          ? AppBeveledRectangleBorder(
                              side: BorderSide.none,
                              bevelSize: bevel,
                              borderRadius: BorderRadius.circular(corner),
                            )
                          : RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                    ),
                  ),
                )
              else
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () =>
                        ref.read(waStatusProvider.notifier).logout(),
                    icon: const Icon(Icons.logout),
                    label: Text(l10n.disconnectInstance),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: accent,
                      side: BorderSide(color: accent),
                      minimumSize: const Size(0, 56),
                      shape: bevel > 0
                          ? AppBeveledRectangleBorder(
                              side: BorderSide(color: accent),
                              bevelSize: bevel,
                              borderRadius: BorderRadius.circular(corner),
                            )
                          : RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
    );

    if (bevel > 0) {
      cardContent = Container(
        decoration: ShapeDecoration(
          color: accent.withValues(alpha: (isDark ? 0.05 : 0.1) * opacity),
          shadows: glowIntensity > 0
              ? [
                  BoxShadow(
                    color: accent.withValues(alpha: isDark ? 0.05 : 0.1),
                    blurRadius: glowIntensity,
                    spreadRadius: 0,
                  ),
                ]
              : null,
          shape: AppBeveledRectangleBorder(
            side: BorderSide(
              color: accent.withValues(alpha: isDark ? 0.2 : 0.4),
              width: 2,
            ),
            bevelSize: bevel,
            borderRadius: BorderRadius.circular(corner),
          ),
        ),
        child: cardContent,
      );
    }

    if (blur > 0) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(corner),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
          child: cardContent,
        ),
      );
    }

    return cardContent;
  }

  void _showPairingDialog(BuildContext context, WidgetRef ref) {
    showDialog(context: context, builder: (context) => const PairingDialog());
  }
}

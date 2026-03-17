import 'package:g777_client/shared/painters/custom_painters.dart';
import 'package:flutter/services.dart';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/shared/providers/logs_provider.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'package:g777_client/core/theme/theme.dart'; // Unified theme system

class LiveTelemetryWidget extends ConsumerWidget {
  const LiveTelemetryWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final logs = ref.watch(logsProvider);
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;
    final l10n = AppLocalizations.of(context)!;
    final extension = theme.extension<G777ThemeExtension>();

    final double blur = extension?.glassBlur ?? 0.0;
    final double opacity = extension?.glassOpacity ?? 1.0;
    final double corner = extension?.edgeRadius ?? 20.0;
    final double bevel = extension?.cutCornerSize ?? 0.0;

    Widget terminalContent = Container(
      height: 300,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: isDark
            ? colors.surfaceContainerHighest.withValues(alpha: 0.35 * opacity)
            : colors.surfaceContainer.withValues(alpha: opacity),
        borderRadius: bevel > 0 ? null : BorderRadius.circular(corner),
        border: bevel > 0
            ? null
            : Border.all(color: colors.outline.withValues(alpha: 0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.terminal, size: 14, color: colors.telemetryGreen),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  l10n.liveTelemetry,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                    color: colors.telemetryGreen,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              if (logs.isNotEmpty)
                IconButton(
                  icon: Icon(
                    Icons.copy_all_rounded,
                    size: 14,
                    color: colors.telemetryGreen.withValues(alpha: 0.6),
                  ),
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  onPressed: () {
                    final allLogs = logs
                        .map(
                          (l) =>
                              "[${l.timestamp.hour}:${l.timestamp.minute}:${l.timestamp.second}] ${l.message}",
                        )
                        .join("\n");
                    Clipboard.setData(ClipboardData(text: allLogs));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('All logs copied to clipboard'),
                        duration: Duration(seconds: 1),
                      ),
                    );
                  },
                  tooltip: 'Copy All Logs',
                ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: logs.isEmpty
                ? Center(
                    child: Text(
                      'No system activity',
                      style: TextStyle(
                        fontSize: 11,
                        color: colors.onSurface.withValues(alpha: 0.4),
                      ),
                    ),
                  )
                : ListView.builder(
                    itemCount: logs.length,
                    reverse: true,
                    itemBuilder: (context, index) {
                      final log = logs[index];
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '${log.timestamp.hour.toString().padLeft(2, '0')}:${log.timestamp.minute.toString().padLeft(2, '0')}:${log.timestamp.second.toString().padLeft(2, '0')} > ',
                              style: TextStyle(
                                fontSize: 11,
                                fontFamily: 'monospace',
                                color: colors.onSurface.withValues(alpha: 0.55),
                              ),
                            ),
                            Expanded(
                              child: SelectableText(
                                log.message,
                                style: TextStyle(
                                  fontSize: 11,
                                  fontFamily: 'monospace',
                                  color: colors.onSurface.withValues(
                                    alpha: 0.8,
                                  ),
                                ),
                                maxLines: 2,
                              ),
                            ),
                            IconButton(
                              icon: Icon(
                                Icons.copy_rounded,
                                size: 10,
                                color: colors.onSurface.withValues(alpha: 0.3),
                              ),
                              padding: EdgeInsets.zero,
                              constraints: const BoxConstraints(),
                              onPressed: () {
                                Clipboard.setData(
                                  ClipboardData(text: log.message),
                                );
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Line copied'),
                                    duration: Duration(milliseconds: 500),
                                  ),
                                );
                              },
                            ),
                          ],
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );

    if (bevel > 0) {
      terminalContent = Container(
        decoration: ShapeDecoration(
          color: isDark
              ? colors.surfaceContainerHighest.withValues(alpha: 0.35 * opacity)
              : colors.surfaceContainer.withValues(alpha: opacity),
          shape: AppBeveledRectangleBorder(
            side: BorderSide(
              color: colors.outline.withValues(alpha: 0.1),
              width: 1,
            ),
            bevelSize: bevel,
            borderRadius: BorderRadius.circular(corner),
          ),
        ),
        child: terminalContent,
      );
    }

    if (blur > 0) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(corner),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
          child: terminalContent,
        ),
      );
    }

    return terminalContent;
  }
}

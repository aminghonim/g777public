import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/shared/providers/logs_provider.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'package:g777_client/core/theme/theme.dart'; // Unified theme system

class LogsFooter extends ConsumerWidget {
  const LogsFooter({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final logs = ref.watch(logsProvider);
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      height: 120,
      decoration: BoxDecoration(
        color: isDark ? colorScheme.surface : colorScheme.surfaceContainer,
        border: Border(
          top: BorderSide(
            color: colorScheme.outline.withValues(alpha: 0.1),
            width: 1,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
            child: Row(
              children: [
                Icon(
                  Icons.terminal_rounded,
                  size: 14,
                  color: colorScheme.telemetryGreen,
                ),
                const SizedBox(width: 8),
                Text(
                  l10n.systemLogs.toUpperCase(),
                  style: TextStyle(
                    color: colorScheme.onSurface.withValues(alpha: 0.7),
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.2,
                  ),
                ),
                const Spacer(),
                IconButton(
                  icon: Icon(
                    Icons.cleaning_services_rounded,
                    size: 14,
                    color: colorScheme.onSurface.withValues(alpha: 0.4),
                  ),
                  onPressed: () => ref.read(logsProvider.notifier).clearLogs(),
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  visualDensity: VisualDensity.compact,
                ),
              ],
            ),
          ),
          Expanded(
            child: Container(
              margin: const EdgeInsets.all(8),
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: colorScheme.onSurface.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(4),
              ),
              child: logs.isEmpty
                  ? Center(
                      child: Text(
                        l10n.awaitingCommands,
                        style: TextStyle(
                          color: colorScheme.onSurface.withValues(alpha: 0.1),
                          fontSize: 10,
                        ),
                      ),
                    )
                  : ListView.builder(
                      reverse: false, // Provider already has latest first
                      itemCount: logs.length,
                      itemBuilder: (context, index) {
                        final log = logs[index];
                        Color logColor = colorScheme.telemetryGreen;

                        if (log.type == LogType.error) {
                          logColor = colorScheme.error;
                        }
                        if (log.type == LogType.warning) {
                          logColor = colorScheme.statusWarning;
                        }
                        if (log.type == LogType.info) {
                          logColor = colorScheme.onSurface.withValues(
                            alpha: 0.6,
                          );
                        }

                        return Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '[${log.timestamp.toString().split(' ')[1].split('.')[0]}]',
                                style: TextStyle(
                                  color: colorScheme.onSurface.withValues(
                                    alpha: 0.3,
                                  ),
                                  fontSize: 11,
                                  fontFamily: 'monospace',
                                ),
                              ),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  log.message,
                                  style: TextStyle(
                                    color: logColor,
                                    fontSize: 11,
                                    fontFamily: 'monospace',
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

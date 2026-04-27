import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/theme/theme.dart';
import 'package:g777_client/shared/providers/logs_provider.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'dart:ui';

class GlobalLogsConsole extends ConsumerStatefulWidget {
  const GlobalLogsConsole({super.key});

  @override
  ConsumerState<GlobalLogsConsole> createState() => _GlobalLogsConsoleState();
}

class _GlobalLogsConsoleState extends ConsumerState<GlobalLogsConsole> {
  final ScrollController _scrollController = ScrollController();
  bool _autoScroll = true;
  double _dragHeight = 150.0;
  final double _minHeight = 40.0;
  final double _maxHeight = 600.0;

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_autoScroll && _scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final logs = ref.watch(filteredLogsProvider);
    final consoleState = ref.watch(consoleStateProvider);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final extension = theme.extension<G777ThemeExtension>();
    final l10n = AppLocalizations.of(context)!;

    double currentHeight;
    switch (consoleState) {
      case ConsoleState.minimized:
        currentHeight = _minHeight;
        break;
      case ConsoleState.normal:
        currentHeight = _dragHeight;
        break;
      case ConsoleState.expanded:
        currentHeight = 400.0;
        break;
      case ConsoleState.full:
        currentHeight = MediaQuery.of(context).size.height * 0.8;
        break;
    }

    WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());

    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOutQuart,
      height: currentHeight,
      width: double.infinity,
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor.withValues(
          alpha: extension?.glassOpacity ?? 0.8,
        ),
        border: Border(
          top: BorderSide(
            color: colorScheme.primary.withValues(alpha: 0.3),
            width: 1.5,
          ),
        ),
      ),
      child: Stack(
        children: [
          if (extension?.glassBlur != null && extension!.glassBlur > 0)
            Positioned.fill(
              child: BackdropFilter(
                filter: ImageFilter.blur(
                  sigmaX: extension.glassBlur,
                  sigmaY: extension.glassBlur,
                ),
                child: Container(color: Colors.transparent),
              ),
            ),
          Column(
            children: [
              GestureDetector(
                onVerticalDragUpdate: (details) {
                  setState(() {
                    _dragHeight = (_dragHeight - details.delta.dy).clamp(
                      _minHeight,
                      _maxHeight,
                    );
                    ref
                        .read(consoleStateProvider.notifier)
                        .set(ConsoleState.normal);
                  });
                },
                child: Container(
                  height: 32,
                  width: double.infinity,
                  color: colorScheme.primary.withValues(alpha: 0.05),
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Row(
                    children: [
                      Icon(
                        Icons.terminal_rounded,
                        size: 14,
                        color: colorScheme.primary,
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
                      _ConsoleAction(
                        icon: _autoScroll
                            ? Icons.arrow_downward_rounded
                            : Icons.pause_circle_outline_rounded,
                        onTap: () =>
                            setState(() => _autoScroll = !_autoScroll),
                        isActive: _autoScroll,
                        tooltip: 'Auto-scroll',
                      ),
                      _ConsoleAction(
                        icon: Icons.cleaning_services_rounded,
                        onTap: () =>
                            ref.read(logsProvider.notifier).clearLogs(),
                        tooltip: 'Clear Logs',
                      ),
                      _ConsoleAction(
                        icon: consoleState == ConsoleState.minimized
                            ? Icons.keyboard_arrow_up_rounded
                            : Icons.keyboard_arrow_down_rounded,
                        onTap: () {
                          final next = consoleState == ConsoleState.minimized
                              ? ConsoleState.normal
                              : ConsoleState.minimized;
                          ref
                              .read(consoleStateProvider.notifier)
                              .set(next);
                        },
                      ),
                    ],
                  ),
                ),
              ),
              if (consoleState != ConsoleState.minimized)
                Expanded(
                  child: Container(
                    margin: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: logs.isEmpty
                        ? Center(
                            child: Text(
                              l10n.awaitingCommands,
                              style: TextStyle(
                                color: colorScheme.onSurface.withValues(
                                  alpha: 0.1,
                                ),
                                fontSize: 11,
                              ),
                            ),
                          )
                        : ListView.builder(
                            controller: _scrollController,
                            itemCount: logs.length,
                            itemBuilder: (context, index) {
                              final displayLog =
                                  logs[logs.length - 1 - index];

                              Color logColor;
                              switch (displayLog.type) {
                                case LogType.error:
                                  logColor = colorScheme.error;
                                  break;
                                case LogType.success:
                                  logColor = Colors.greenAccent;
                                  break;
                                case LogType.warning:
                                  logColor = Colors.orangeAccent;
                                  break;
                                default:
                                  logColor = colorScheme.onSurface.withValues(
                                    alpha: 0.8,
                                  );
                              }

                              return Padding(
                                padding: const EdgeInsets.only(bottom: 4),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      '[${displayLog.timestamp.toString().split(' ')[1].split('.')[0]}]',
                                      style: TextStyle(
                                        color: colorScheme.onSurface.withValues(
                                          alpha: 0.2,
                                        ),
                                        fontSize: 11,
                                        fontFamily: 'FiraCode',
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        displayLog.message,
                                        style: TextStyle(
                                          color: logColor,
                                          fontSize: 11,
                                          fontFamily: 'FiraCode',
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
              if (consoleState != ConsoleState.minimized) _FilterBar(),
            ],
          ),
        ],
      ),
    );
  }
}

class _FilterBar extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final filter = ref.watch(logsFilterProvider);
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      height: 36,
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(
            color: colorScheme.outline.withValues(alpha: 0.05),
          ),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              onChanged: (val) => ref
                  .read(logsFilterProvider.notifier)
                  .update((f) => f.copyWith(query: val)),
              style: const TextStyle(fontSize: 11),
              decoration: InputDecoration(
                hintText: 'Search logs...',
                border: InputBorder.none,
                hintStyle: TextStyle(
                  color: colorScheme.onSurface.withValues(alpha: 0.2),
                ),
                isDense: true,
              ),
            ),
          ),
          const VerticalDivider(width: 20, indent: 8, endIndent: 8),
          _FilterChip(
            label: 'Info',
            type: LogType.info,
            isActive: filter.activeTypes.contains(LogType.info),
          ),
          _FilterChip(
            label: 'Error',
            type: LogType.error,
            isActive: filter.activeTypes.contains(LogType.error),
          ),
          _FilterChip(
            label: 'Success',
            type: LogType.success,
            isActive: filter.activeTypes.contains(LogType.success),
          ),
        ],
      ),
    );
  }
}

class _FilterChip extends ConsumerWidget {
  final String label;
  final LogType type;
  final bool isActive;

  const _FilterChip({
    required this.label,
    required this.type,
    required this.isActive,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colorScheme = Theme.of(context).colorScheme;
    return GestureDetector(
      onTap: () {
        final nextTypes = Set<LogType>.from(
          ref.read(logsFilterProvider).activeTypes,
        );
        if (isActive) {
          nextTypes.remove(type);
        } else {
          nextTypes.add(type);
        }
        ref
            .read(logsFilterProvider.notifier)
            .update((f) => f.copyWith(activeTypes: nextTypes));
      },
      child: Container(
        margin: const EdgeInsets.only(left: 8),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
        decoration: BoxDecoration(
          color: isActive
              ? colorScheme.primary.withValues(alpha: 0.2)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(4),
          border: Border.all(
            color: isActive
                ? colorScheme.primary
                : colorScheme.outline.withValues(alpha: 0.1),
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 9,
            color: isActive
                ? colorScheme.primary
                : colorScheme.onSurface.withValues(alpha: 0.4),
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}

class _ConsoleAction extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  final bool isActive;
  final String? tooltip;

  const _ConsoleAction({
    required this.icon,
    required this.onTap,
    this.isActive = false,
    this.tooltip,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return IconButton(
      icon: Icon(
        icon,
        size: 14,
        color: isActive
            ? colorScheme.primary
            : colorScheme.onSurface.withValues(alpha: 0.4),
      ),
      onPressed: onTap,
      tooltip: tooltip,
      padding: const EdgeInsets.all(4),
      constraints: const BoxConstraints(),
    );
  }
}

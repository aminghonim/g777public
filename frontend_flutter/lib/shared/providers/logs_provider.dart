import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/providers/system_stream_provider.dart';

/// Log Levels
enum LogType { info, success, error, warning }

/// Single Log Entry
class LogEntry {
  final DateTime timestamp;
  final String message;
  final LogType type;

  LogEntry({
    required this.timestamp,
    required this.message,
    this.type = LogType.info,
  });
}

/// Global Logs Buffer (Unified singleton pipeline)
class LogsNotifier extends Notifier<List<LogEntry>> {
  @override
  List<LogEntry> build() => [];

  void addLog(String message, {LogType type = LogType.info}) {
    if (state.isNotEmpty && state.first.message == message) return;

    state = [
      LogEntry(timestamp: DateTime.now(), message: message, type: type),
      ...state,
    ];

    if (state.length > 500) {
      state = state.sublist(0, 500);
    }
  }

  void clearLogs() => state = [];
}

final logsProvider = NotifierProvider<LogsNotifier, List<LogEntry>>(
  LogsNotifier.new,
);

/// --- Filter Logic ---

class LogsFilter {
  final String query;
  final Set<LogType> activeTypes;
  final bool isPaused;

  LogsFilter({
    this.query = '',
    this.activeTypes = const {
      LogType.info,
      LogType.success,
      LogType.error,
      LogType.warning,
    },
    this.isPaused = false,
  });

  LogsFilter copyWith({
    String? query,
    Set<LogType>? activeTypes,
    bool? isPaused,
  }) {
    return LogsFilter(
      query: query ?? this.query,
      activeTypes: activeTypes ?? this.activeTypes,
      isPaused: isPaused ?? this.isPaused,
    );
  }
}

final logsFilterProvider = NotifierProvider<LogsFilterNotifier, LogsFilter>(
  LogsFilterNotifier.new,
);

class LogsFilterNotifier extends Notifier<LogsFilter> {
  @override
  LogsFilter build() => LogsFilter();

  void update(LogsFilter Function(LogsFilter) updater) {
    state = updater(state);
  }
}

final filteredLogsProvider = Provider<List<LogEntry>>((ref) {
  final logs = ref.watch(logsProvider);
  final filter = ref.watch(logsFilterProvider);

  if (filter.isPaused) return [];

  return logs.where((log) {
    final matchesQuery = log.message.toLowerCase().contains(
      filter.query.toLowerCase(),
    );
    final matchesType = filter.activeTypes.contains(log.type);
    return matchesQuery && matchesType;
  }).toList();
});

/// --- UI State Providers ---

enum ConsoleState { minimized, normal, expanded, full }

final consoleStateProvider = NotifierProvider<ConsoleStateNotifier, ConsoleState>(
  ConsoleStateNotifier.new,
);

class ConsoleStateNotifier extends Notifier<ConsoleState> {
  @override
  ConsoleState build() => ConsoleState.normal;

  void set(ConsoleState value) => state = value;
}

/// Unified Log Listener (Gap 2 Compliance)
final logsStreamListenerProvider = Provider<void>((ref) {
  final filter = ref.watch(logsFilterProvider);

  ref.listen(logsStreamProvider, (prev, next) {
    if (filter.isPaused) return;

    next.whenData((event) {
      if (event['type'] == 'LOG') {
        final data = event['data'];
        if (data != null && data['message'] != null) {
          final levelStr = data['level']?.toString().toLowerCase() ?? 'info';
          LogType type = LogType.info;
          if (levelStr == 'error') type = LogType.error;
          if (levelStr == 'success') type = LogType.success;
          if (levelStr == 'warning') type = LogType.warning;

          ref
              .read(logsProvider.notifier)
              .addLog(data['message'].toString(), type: type);
        }
      } else if (event['type'] == 'CAMPAIGN') {
        final data = event['data'];
        if (data != null && data['logs'] != null) {
          final List<dynamic> logs = data['logs'];
          if (logs.isNotEmpty) {
            ref
                .read(logsProvider.notifier)
                .addLog(logs.last.toString(), type: LogType.info);
          }
        }
      }
    });
  });
});

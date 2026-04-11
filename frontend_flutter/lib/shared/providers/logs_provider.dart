import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers/system_stream_provider.dart';

/// Global Logs Provider
final logsProvider = StateNotifierProvider<LogsNotifier, List<LogEntry>>((ref) {
  return LogsNotifier();
});

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

enum LogType { info, success, error, warning }

class LogsNotifier extends StateNotifier<List<LogEntry>> {
  LogsNotifier() : super([]);

  void addLog(String message, {LogType type = LogType.info}) {
    if (state.isNotEmpty && state.first.message == message) return;

    state = [
      LogEntry(timestamp: DateTime.now(), message: message, type: type),
      ...state,
    ];

    if (state.length > 100) {
      state = state.sublist(0, 100);
    }
  }

  void clearLogs() {
    state = [];
  }
}

/// Unified Log Listener
final logsStreamListenerProvider = Provider<void>((ref) {
  ref.listen(logsStreamProvider, (prev, next) {
    next.whenData((event) {
      if (event['type'] == 'LOG') {
        final data = event['data'];
        if (data != null && data['message'] != null) {
          final levelStr = data['level']?.toString().toLowerCase() ?? 'info';
          LogType type = LogType.info;
          if (levelStr == 'error') type = LogType.error;
          if (levelStr == 'success') type = LogType.success;
          if (levelStr == 'warning') type = LogType.warning;

          ref.read(logsProvider.notifier).addLog(
                data['message'].toString(),
                type: type,
              );
        }
      }
    });
  });
});

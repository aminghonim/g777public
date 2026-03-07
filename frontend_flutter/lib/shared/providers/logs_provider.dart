import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/providers/system_stream_provider.dart';

/// Global Logs Provider
/// Manages platform-wide system logs in a unified singleton pipeline.
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
    // Basic deduplication for immediate successive logs
    if (state.isNotEmpty && state.first.message == message) return;

    state = [
      LogEntry(timestamp: DateTime.now(), message: message, type: type),
      ...state,
    ];

    // Maintain buffer of last 100 entries
    if (state.length > 100) {
      state = state.sublist(0, 100);
    }
  }

  void clearLogs() {
    state = [];
  }
}

/// Unified Log Listener (Gap 2 Compliance).
/// Attaches to the global SSE pipeline to capture and record logs from
/// all system modules (Campaigns, API, System Checks).
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

          ref
              .read(logsProvider.notifier)
              .addLog(data['message'].toString(), type: type);
        }
      } else if (event['type'] == 'CAMPAIGN') {
        // Also capture legacy campaign logs if present
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

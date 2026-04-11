import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';

/// Unified Singleton SSE Pipeline (Gap 2 Compliance).
final systemStreamProvider = StreamProvider<Map<String, dynamic>>((ref) {
  final api = ref.watch(apiClientProvider);
  return api.streamGet('/system/stream/events');
});

final logsStreamProvider = StreamProvider<Map<String, dynamic>>((ref) async* {
  final stream = ref.watch(systemStreamProvider.stream);
  await for (final event in stream) {
    if (event['type'] == 'LOG') yield event;
  }
});

final whatsappStatusStreamProvider = StreamProvider<Map<String, dynamic>>((ref) async* {
  final stream = ref.watch(systemStreamProvider.stream);
  await for (final event in stream) {
    if (event['type'] == 'STATUS') yield event;
  }
});

final campaignStreamProvider = StreamProvider<Map<String, dynamic>>((ref) async* {
  final stream = ref.watch(systemStreamProvider.stream);
  await for (final event in stream) {
    if (event['type'] == 'CAMPAIGN') yield event;
  }
});

final telemetryStreamProvider = StreamProvider<Map<String, dynamic>>((ref) async* {
  final stream = ref.watch(systemStreamProvider.stream);
  await for (final event in stream) {
    if (event['type'] == 'TELEMETRY') yield event;
  }
});

final quotaStreamProvider = StreamProvider<Map<String, dynamic>>((ref) async* {
  final stream = ref.watch(systemStreamProvider.stream);
  await for (final event in stream) {
    if (event['type'] == 'QUOTA') yield event;
  }
});

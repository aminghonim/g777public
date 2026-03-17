import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';

/// Unified Singleton SSE Pipeline (Gap 2 Compliance).
///
/// Minimizes OS connection overhead by maintaining a single persistent
/// connection to the backend event broker. All system-wide events
/// are routed through this pipe.
final systemStreamProvider = StreamProvider<Map<String, dynamic>>((ref) {
  final api = ref.watch(apiClientProvider);

  // Connect to the synchronized backend stream once for the entire session.
  return api.streamGet('/system/stream/events');
});

/// --- Specialized Routed Streams ---
/// These providers act as "virtual channels" that filter the main stream.

/// Unified Logger Channel
/// Routes all system logs to the UI.
final logsStreamProvider = StreamProvider<Map<String, dynamic>>((ref) async* {
  await for (final event in ref.watch(systemStreamProvider.future).asStream()) {
    if (event['type'] == 'LOG') yield event;
  }
});

/// WhatsApp Instance Status Channel
/// Essential for the InstanceConnectionWidget and Dashboard cards.
final whatsappStatusStreamProvider = StreamProvider<Map<String, dynamic>>((
  ref,
) async* {
  await for (final event in ref.watch(systemStreamProvider.future).asStream()) {
    if (event['type'] == 'STATUS') yield event;
  }
});

/// Active Campaign Data Channel
/// Routes progress and final summaries to the GroupSenderController.
final campaignStreamProvider = StreamProvider<Map<String, dynamic>>((
  ref,
) async* {
  await for (final event in ref.watch(systemStreamProvider.future).asStream()) {
    if (event['type'] == 'CAMPAIGN') yield event;
  }
});

/// Hardware & Performance Channel
/// Routes CPU/RAM metrics to the TelemetryWidgets.
final telemetryStreamProvider = StreamProvider<Map<String, dynamic>>((
  ref,
) async* {
  await for (final event in ref.watch(systemStreamProvider.future).asStream()) {
    if (event['type'] == 'TELEMETRY') yield event;
  }
});

/// User Quota & Billing Channel
/// Updates the QuotaDashboardWidget in real-time.
final quotaStreamProvider = StreamProvider<Map<String, dynamic>>((ref) async* {
  await for (final event in ref.watch(systemStreamProvider.future).asStream()) {
    if (event['type'] == 'QUOTA') yield event;
  }
});

/// Auto-Resume Campaign Channel
/// Routes connection-loss pause/resume events to AutoResumeBanner.
final autoResumeStreamProvider = StreamProvider<Map<String, dynamic>>((
  ref,
) async* {
  await for (final event in ref.watch(systemStreamProvider.future).asStream()) {
    if (event['type'] == 'AUTO_RESUME') yield event;
  }
});

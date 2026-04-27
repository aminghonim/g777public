import 'package:flutter/material.dart';
import 'package:g777_client/core/services/api_service.dart';
import 'package:g777_client/core/theme/theme.dart'; // Unified theme system

class ScraplingStatusChip extends StatefulWidget {
  const ScraplingStatusChip({super.key});

  @override
  State<ScraplingStatusChip> createState() => _ScraplingStatusChipState();
}

class _ScraplingStatusChipState extends State<ScraplingStatusChip> {
  final ApiService _api = ApiService();
  late Future<_HealthSnapshot> _future;

  @override
  void initState() {
    super.initState();
    _future = _fetchHealth();
  }

  Future<_HealthSnapshot> _fetchHealth() async {
    final sw = Stopwatch()..start();
    final data = await _api.checkHealth();
    sw.stop();
    return _HealthSnapshot(
      data: data,
      requestLatencyMs: sw.elapsedMilliseconds,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return FutureBuilder<_HealthSnapshot>(
      future: _future,
      builder: (context, snapshot) {
        String label = 'SCRAPLING CHECKING';
        Color statusColor = colorScheme.statusInfo;
        int? latencyMs;

        if (snapshot.connectionState == ConnectionState.waiting) {
          label = 'SCRAPLING CHECKING';
          statusColor = colorScheme.statusInfo;
        } else if (snapshot.hasError) {
          label = 'SCRAPLING ERROR';
          statusColor = colorScheme.statusError;
        } else if (snapshot.hasData) {
          final data = snapshot.data!.data;
          latencyMs = snapshot.data!.requestLatencyMs;
          final status = (data['status'] ?? '').toString().toLowerCase();
          final mode = (data['mode'] ?? '').toString().toLowerCase();

          final isReady = status == 'healthy' && mode.contains('scrapling');

          if (isReady) {
            label = 'SCRAPLING READY';
            statusColor = colorScheme.statusOnline;
          } else {
            label = 'SCRAPLING FALLBACK';
            statusColor = colorScheme.statusWarning;
          }
        }

        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          margin: const EdgeInsets.only(right: 8),
          decoration: BoxDecoration(
            color: statusColor.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: statusColor.withValues(alpha: 0.5)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: statusColor,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: statusColor.withValues(alpha: 0.5),
                      blurRadius: 8,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Text(
                label,
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                  color: colorScheme.onSurface.withValues(alpha: 0.7),
                  fontFamily: 'Oxanium',
                ),
              ),
              if (latencyMs != null) ...[
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 4,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: colorScheme.surfaceContainerHighest.withValues(
                      alpha: 0.5,
                    ),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    '${latencyMs}ms',
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.bold,
                      color: latencyMs <= 500
                          ? colorScheme.statusOnline
                          : colorScheme.statusWarning,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}

class _HealthSnapshot {
  final Map<String, dynamic> data;
  final int requestLatencyMs;
  const _HealthSnapshot({required this.data, required this.requestLatencyMs});
}

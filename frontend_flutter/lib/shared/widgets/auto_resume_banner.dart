import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/providers/system_stream_provider.dart';
import 'package:g777_client/core/theme/semantic_colors.dart';

/// Animated banner showing auto-resume status when campaign pauses
/// due to connection loss.
class AutoResumeBanner extends ConsumerWidget {
  const AutoResumeBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final autoResumeAsync = ref.watch(autoResumeStreamProvider);

    return autoResumeAsync.when(
      data: (event) {
        final data = event['data'] as Map<String, dynamic>?;
        final status = data?['status'] as String?;
        final retryCount = data?['retry_count'] as int? ?? 0;
        final maxRetries = data?['max_retries'] as int? ?? 5;
        final nextRetryIn = data?['next_retry_in_seconds'] as int?;

        if (status != 'paused' && status != 'reconnecting') {
          return const SizedBox.shrink();
        }

        return AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          margin: const EdgeInsets.only(bottom: 16),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: colorScheme.statusWarning.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: colorScheme.statusWarning.withValues(alpha: 0.5),
              width: 1.5,
            ),
            boxShadow: [
              BoxShadow(
                color: colorScheme.statusWarning.withValues(alpha: 0.2),
                blurRadius: 10,
                spreadRadius: 2,
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  _buildPulsingDot(colorScheme.statusWarning),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          status == 'reconnecting'
                              ? 'RECONNECTING & PAUSED...'
                              : 'CAMPAIGN PAUSED - WAITING TO RESUME',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: colorScheme.statusWarning,
                            letterSpacing: 1,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'Connection lost. The app will automatically resume when connection is restored.',
                          style: TextStyle(
                            fontSize: 11,
                            color: colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: LinearProgressIndicator(
                      value: retryCount / maxRetries,
                      backgroundColor: colorScheme.outline.withValues(
                        alpha: 0.2,
                      ),
                      valueColor: AlwaysStoppedAnimation<Color>(
                        colorScheme.statusWarning,
                      ),
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'Attempt $retryCount/$maxRetries',
                    style: TextStyle(
                      fontSize: 10,
                      color: colorScheme.onSurfaceVariant,
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
              if (nextRetryIn != null && nextRetryIn > 0) ...[
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.timer,
                      size: 14,
                      color: colorScheme.statusWarning,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Next retry in ${nextRetryIn}s',
                      style: TextStyle(
                        fontSize: 11,
                        color: colorScheme.statusWarning,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton.icon(
                    onPressed: () {
                      // Manual resume action
                    },
                    icon: Icon(
                      Icons.play_arrow,
                      size: 16,
                      color: colorScheme.statusWarning,
                    ),
                    label: Text(
                      'RESUME NOW',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: colorScheme.statusWarning,
                      ),
                    ),
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      side: BorderSide(
                        color: colorScheme.statusWarning.withValues(alpha: 0.5),
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(6),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (_, _) => const SizedBox.shrink(),
    );
  }

  Widget _buildPulsingDot(Color color) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.0, end: 1.0),
      duration: const Duration(milliseconds: 1000),
      curve: Curves.easeInOut,
      builder: (context, value, child) {
        return Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.3 + (value * 0.7)),
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: color.withValues(alpha: 0.5 * value),
                blurRadius: 8 + (value * 4),
                spreadRadius: 2 * value,
              ),
            ],
          ),
        );
      },
    );
  }
}

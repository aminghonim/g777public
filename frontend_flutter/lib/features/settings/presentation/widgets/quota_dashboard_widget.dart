import 'package:flutter/material.dart';
import '../../../../core/theme/theme_extensions.dart';

class QuotaDashboardWidget extends StatelessWidget {
  const QuotaDashboardWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final ext = theme.extension<G777ThemeExtension>();
    final colors = theme.colorScheme;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colors.surfaceContainer,
        borderRadius: BorderRadius.circular(ext?.edgeRadius ?? 24),
        border: Border.all(color: colors.outline.withValues(alpha: 0.1)),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'SYSTEM QUOTA',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, letterSpacing: 2),
          ),
          SizedBox(height: 24),
          _QuotaRow(label: 'MESSAGES', current: 1450, total: 5000, color: Colors.blueAccent),
          SizedBox(height: 16),
          _QuotaRow(label: 'INSTANCES', current: 2, total: 5, color: Colors.greenAccent),
        ],
      ),
    );
  }
}

class _QuotaRow extends StatelessWidget {
  final String label;
  final int current;
  final int total;
  final Color color;

  const _QuotaRow({
    required this.label,
    required this.current,
    required this.total,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final progress = current / total;
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
            Text('$current / $total', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w900)),
          ],
        ),
        const SizedBox(height: 8),
        LinearProgressIndicator(
          value: progress,
          backgroundColor: color.withValues(alpha: 0.1),
          color: color,
          minHeight: 6,
          borderRadius: BorderRadius.circular(3),
        ),
      ],
    );
  }
}

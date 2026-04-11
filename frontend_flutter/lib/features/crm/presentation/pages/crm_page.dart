import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class CrmPage extends ConsumerWidget {
  const CrmPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.people_alt_rounded, size: 64, color: theme.colorScheme.primary),
            const SizedBox(height: 16),
            const Text(
              'CRM COMMAND CENTER',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                fontFamily: 'Oxanium',
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'COMING SOON',
              style: TextStyle(
                fontSize: 12,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
                letterSpacing: 4,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

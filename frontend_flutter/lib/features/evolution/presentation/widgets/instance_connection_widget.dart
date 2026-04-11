import 'package:flutter/material.dart';

class InstanceConnectionWidget extends StatelessWidget {
  const InstanceConnectionWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: colorScheme.outline.withValues(alpha: 0.1)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: colorScheme.primary.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.hub_rounded, color: colorScheme.primary),
          ),
          const SizedBox(width: 16),
          const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'EVOLUTION NODE',
                style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1),
              ),
              Text(
                'PROXIED: v1.1.2',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w900, fontFamily: 'Oxanium'),
              ),
            ],
          ),
          const Spacer(),
          ElevatedButton(
            onPressed: () {},
            style: ElevatedButton.styleFrom(
              backgroundColor: colorScheme.surface,
              foregroundColor: colorScheme.primary,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('MANAGE'),
          ),
        ],
      ),
    );
  }
}

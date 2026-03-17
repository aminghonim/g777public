import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/evolution_provider.dart';

/// SAAS-011: Advanced Connection Dashboard Widget.
/// Strictly decoupled UI that observes the Evolution logic state.
class EvolutionDashboardWidget extends ConsumerWidget {
  const EvolutionDashboardWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final evolutionAsync = ref.watch(evolutionControllerProvider);

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface.withAlpha(25),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: Theme.of(context).colorScheme.primary.withAlpha(50),
          width: 1,
        ),
      ),
      child: evolutionAsync.when(
        data: (state) => _buildUIForState(context, ref, state),
        loading: () => const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text(
                'Initializing Secure Connection...',
                style: TextStyle(letterSpacing: 1.2),
              ),
            ],
          ),
        ),
        error: (error, _) => _ErrorStateUI(
          message: error.toString(),
          onRetry: () => ref
              .read(evolutionControllerProvider.notifier)
              .initializeConnection(),
        ),
      ),
    );
  }

  Widget _buildUIForState(
    BuildContext context,
    WidgetRef ref,
    EvolutionState state,
  ) {
    return switch (state) {
      EvolutionInitial() => _InitialStateUI(
        onConnect: () => ref
            .read(evolutionControllerProvider.notifier)
            .initializeConnection(),
      ),
      EvolutionLoading() => const Center(child: CircularProgressIndicator()),
      EvolutionQRReceived(qrBase64: final qr) => _QRReceivedStateUI(
        qrBase64: qr,
      ),
      EvolutionConnected() => _ConnectedStateUI(
        onDisconnect: () =>
            ref.read(evolutionControllerProvider.notifier).disconnect(),
      ),
      EvolutionError(message: final msg) => _ErrorStateUI(
        message: msg,
        onRetry: () => ref
            .read(evolutionControllerProvider.notifier)
            .initializeConnection(),
      ),
    };
  }
}

class _InitialStateUI extends StatelessWidget {
  final VoidCallback onConnect;

  const _InitialStateUI({required this.onConnect});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          Icons.phonelink_setup_rounded,
          size: 64,
          color: Theme.of(context).colorScheme.primary,
        ),
        const SizedBox(height: 16),
        const Text(
          'WhatsApp Integration',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        SelectableText(
          'Provision a secure instance to start sending messages.',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Theme.of(context).colorScheme.onSurface.withAlpha(150),
          ),
        ),
        const SizedBox(height: 24),
        ElevatedButton.icon(
          onPressed: onConnect,
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          icon: const Icon(Icons.bolt_rounded),
          label: const Text('CONNECT WHATSAPP'),
        ),
      ],
    );
  }
}

class _QRReceivedStateUI extends StatelessWidget {
  final String qrBase64;

  const _QRReceivedStateUI({required this.qrBase64});

  @override
  Widget build(BuildContext context) {
    final String cleanBase64 = qrBase64.contains(',')
        ? qrBase64.split(',').last
        : qrBase64;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Text(
          'Link Device',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Image.memory(
            base64Decode(cleanBase64),
            width: 250,
            height: 250,
            errorBuilder: (context, error, stackTrace) => const SizedBox(
              width: 250,
              height: 250,
              child: Center(child: Icon(Icons.broken_image_rounded, size: 64)),
            ),
          ),
        ),
        const SizedBox(height: 16),
        const SelectableText(
          'Scan this QR code with your WhatsApp',
          style: TextStyle(fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 8),
        SelectableText(
          'Open WhatsApp > Settings > Linked Devices > Link a Device',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 12,
            color: Theme.of(context).colorScheme.onSurface.withAlpha(150),
          ),
        ),
      ],
    );
  }
}

class _ConnectedStateUI extends StatelessWidget {
  final VoidCallback onDisconnect;

  const _ConnectedStateUI({required this.onDisconnect});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.green.withAlpha(30),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.check_circle_rounded,
            size: 64,
            color: Colors.green,
          ),
        ),
        const SizedBox(height: 16),
        const SelectableText(
          'WhatsApp is Connected',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const SelectableText(
          'Your secure instance is running and healthy.',
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 24),
        OutlinedButton.icon(
          onPressed: onDisconnect,
          style: OutlinedButton.styleFrom(
            foregroundColor: Theme.of(context).colorScheme.error,
            side: BorderSide(color: Theme.of(context).colorScheme.error),
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          ),
          icon: const Icon(Icons.power_settings_new_rounded),
          label: const Text('DISCONNECT'),
        ),
      ],
    );
  }
}

class _ErrorStateUI extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorStateUI({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          Icons.error_outline_rounded,
          size: 48,
          color: Theme.of(context).colorScheme.error,
        ),
        const SizedBox(height: 16),
        SelectableText(
          'Connection Error',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Theme.of(context).colorScheme.error,
          ),
        ),
        const SizedBox(height: 8),
        SelectableText(
          message,
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 14),
        ),
        const SizedBox(height: 24),
        ElevatedButton.icon(
          onPressed: onRetry,
          icon: const Icon(Icons.refresh_rounded),
          label: const Text('RETRY CONNECTION'),
        ),
      ],
    );
  }
}

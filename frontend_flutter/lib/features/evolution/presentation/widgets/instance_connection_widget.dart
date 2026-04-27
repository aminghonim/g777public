import 'dart:convert';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/features/evolution/providers/evolution_provider.dart';
import '../../../../core/theme/theme_extensions.dart';
import 'package:g777_client/core/theme/semantic_colors.dart';

class InstanceConnectionWidget extends ConsumerWidget {
  const InstanceConnectionWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final evolutionAsync = ref.watch(evolutionControllerProvider);
    final theme = Theme.of(context);
    final ext = theme.extension<G777ThemeExtension>();

    return evolutionAsync.when(
      data: (state) => _buildBody(context, ref, state, ext),
      loading: () => _buildLoading(context, ext),
      error: (err, _) => _buildError(context, ref, err.toString(), ext),
    );
  }

  Widget _buildBody(
    BuildContext context,
    WidgetRef ref,
    EvolutionState state,
    G777ThemeExtension? ext,
  ) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final blur = ext?.glassBlur ?? 0.0;
    final opacity = ext?.glassOpacity ?? 1.0;
    final glow = ext?.glowColor;
    final radius = ext?.edgeRadius ?? 24.0;

    Widget content = Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colors.surface.withValues(alpha: 0.05 * opacity),
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(
          color: colors.onSurface.withValues(alpha: 0.1),
          width: 1,
        ),
        boxShadow: glow != null
            ? [
                BoxShadow(
                  color: glow.withValues(alpha: 0.15),
                  blurRadius: ext?.glowIntensity ?? 10.0,
                  spreadRadius: 2,
                ),
              ]
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(context, state),
          const SizedBox(height: 24),
          AnimatedSize(
            duration: const Duration(milliseconds: 300),
            child: _buildContent(context, ref, state, ext),
          ),
        ],
      ),
    );

    if (blur > 0) {
      content = ClipRRect(
        borderRadius: BorderRadius.circular(radius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
          child: content,
        ),
      );
    }

    return content;
  }

  Widget _buildHeader(BuildContext context, EvolutionState state) {
    final colors = Theme.of(context).colorScheme;
    final isConnected = state is EvolutionConnected;

    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: (isConnected ? colors.statusOnline : colors.primary)
                .withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            isConnected ? Icons.check_circle_rounded : Icons.cell_tower_rounded,
            color: isConnected ? colors.statusOnline : colors.primary,
            size: 20,
          ),
        ),
        const SizedBox(width: 12),
        const Text(
          'WHATSAPP TERMINAL',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w900,
            letterSpacing: 2,
            fontFamily: 'Oxanium',
          ),
        ),
        const Spacer(),
        if (isConnected)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: colors.statusOnline.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(
                color: colors.statusOnline.withValues(alpha: 0.3),
              ),
            ),
            child: Text(
              'LIVE',
              style: TextStyle(
                color: colors.statusOnline,
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1,
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildContent(
    BuildContext context,
    WidgetRef ref,
    EvolutionState state,
    G777ThemeExtension? ext,
  ) {
    return switch (state) {
      EvolutionInitial() => _buildInitialState(context, ref),
      EvolutionLoading() => _buildLoadingState(context),
      EvolutionQRReceived(qrBase64: final qr) => _buildQRState(context, qr),
      EvolutionConnected() => _buildConnectedState(context, ref),
      EvolutionError(message: final msg) => _buildErrorState(context, ref, msg),
    };
  }

  Widget _buildInitialState(BuildContext context, WidgetRef ref) {
    final colors = Theme.of(context).colorScheme;
    return Column(
      children: [
        const SizedBox(height: 16),
        Text(
          'SYSTEM READY',
          style: TextStyle(
            color: colors.onSurface.withValues(alpha: 0.4),
            fontSize: 12,
            letterSpacing: 4,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 24),
        Center(
          child: ElevatedButton.icon(
            onPressed: () => ref
                .read(evolutionControllerProvider.notifier)
                .initializeConnection(),
            icon: const Icon(Icons.bolt_rounded, size: 18),
            label: const Text(
              'PROVISION INSTANCE',
              style: TextStyle(
                fontFamily: 'Oxanium',
                fontWeight: FontWeight.bold,
                letterSpacing: 1,
              ),
            ),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
              backgroundColor: colors.primary,
              foregroundColor: colors.onPrimary,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),
      ],
    );
  }

  Widget _buildLoadingState(BuildContext context) {
    return const Center(
      child: Padding(
        padding: EdgeInsets.symmetric(vertical: 40),
        child: CircularProgressIndicator(),
      ),
    );
  }

  Widget _buildQRState(BuildContext context, String qrBase64) {
    final colors = Theme.of(context).colorScheme;
    final String cleanBase64 = qrBase64.contains(',')
        ? qrBase64.split(',').last
        : qrBase64;

    return Column(
      children: [
        const SelectableText(
          'SCAN ENCRYPTED PAYLOAD',
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.bold,
            letterSpacing: 2,
          ),
        ),
        const SizedBox(height: 20),
        Center(
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: colors.surface,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: colors.onSurface.withValues(alpha: 0.1),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.memory(
                base64Decode(cleanBase64),
                width: 200,
                height: 200,
                fit: BoxFit.cover,
              ),
            ),
          ),
        ),
        const SizedBox(height: 24),
        SelectableText(
          'LINK DEVICE THROUGH WHATSAPP SETTINGS',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 10,
            color: colors.onSurface.withValues(alpha: 0.5),
            letterSpacing: 1.5,
          ),
        ),
      ],
    );
  }

  Widget _buildConnectedState(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    return Column(
      children: [
        const SizedBox(height: 16),
        Center(
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: theme.colorScheme.statusOnline.withValues(alpha: 0.05),
              shape: BoxShape.circle,
              border: Border.all(
                color: theme.colorScheme.statusOnline.withValues(alpha: 0.2),
              ),
            ),
            child: Icon(
              Icons.verified_user_rounded,
              size: 48,
              color: theme.colorScheme.statusOnline,
            ),
          ),
        ),
        const SizedBox(height: 20),
        const SelectableText(
          'SECURE SESSION ESTABLISHED',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            letterSpacing: 2,
          ),
        ),
        const SizedBox(height: 32),
        Center(
          child: OutlinedButton.icon(
            onPressed: () =>
                ref.read(evolutionControllerProvider.notifier).disconnect(),
            icon: const Icon(Icons.power_settings_new_rounded, size: 18),
            label: const SelectableText(
              'TERMINATE PORTAL',
              style: TextStyle(
                fontFamily: 'Oxanium',
                fontWeight: FontWeight.bold,
                letterSpacing: 1,
              ),
            ),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 14),
              foregroundColor: theme.colorScheme.error,
              side: BorderSide(
                color: theme.colorScheme.error.withValues(alpha: 0.5),
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),
      ],
    );
  }

  Widget _buildErrorState(BuildContext context, WidgetRef ref, String error) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    return Column(
      children: [
        Icon(Icons.warning_amber_rounded, size: 40, color: colors.statusError),
        const SizedBox(height: 16),
        // SelectableText allows the developer to copy error messages
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: colors.statusError.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: SelectableText(
                  error,
                  textAlign: TextAlign.center,
                  style: TextStyle(color: colors.statusError, fontSize: 13),
                ),
              ),
              IconButton(
                tooltip: 'Copy error',
                icon: Icon(
                  Icons.copy_rounded,
                  size: 16,
                  color: colors.statusError.withValues(alpha: 0.7),
                ),
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: error));
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Error copied to clipboard'),
                      duration: Duration(seconds: 2),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        TextButton.icon(
          onPressed: () =>
              ref.read(evolutionControllerProvider.notifier).retry(),
          icon: const Icon(Icons.refresh_rounded),
          label: const Text('RETRY HANDSHAKE'),
          style: TextButton.styleFrom(
            foregroundColor: theme.colorScheme.primary,
          ),
        ),
      ],
    );
  }

  Widget _buildLoading(BuildContext context, G777ThemeExtension? ext) {
    final colors = Theme.of(context).colorScheme;
    return Container(
      height: 200,
      decoration: BoxDecoration(
        color: colors.onSurface.withValues(alpha: 0.02),
        borderRadius: BorderRadius.circular(ext?.edgeRadius ?? 24),
      ),
      child: const Center(child: CircularProgressIndicator()),
    );
  }

  Widget _buildError(
    BuildContext context,
    WidgetRef ref,
    String error,
    G777ThemeExtension? ext,
  ) {
    final colors = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colors.statusError.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(ext?.edgeRadius ?? 24),
        border: Border.all(color: colors.statusError.withValues(alpha: 0.2)),
      ),
      child: Column(
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: SelectableText(
                  error,
                  style: TextStyle(color: colors.statusError),
                ),
              ),
              IconButton(
                tooltip: 'Copy error',
                icon: Icon(
                  Icons.copy_rounded,
                  size: 16,
                  color: colors.statusError.withValues(alpha: 0.7),
                ),
                onPressed: () {
                  Clipboard.setData(ClipboardData(text: error));
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Error copied to clipboard'),
                      duration: Duration(seconds: 2),
                    ),
                  );
                },
              ),
            ],
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () =>
                ref.read(evolutionControllerProvider.notifier).retry(),
            child: const Text('RETRY'),
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/theme/semantic_colors.dart';
import 'package:g777_client/core/theme/theme_extensions.dart';

import '../providers/warmer_provider.dart';

class WarmerPage extends ConsumerStatefulWidget {
  const WarmerPage({super.key});

  @override
  ConsumerState<WarmerPage> createState() => _WarmerPageState();
}

class _WarmerPageState extends ConsumerState<WarmerPage> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(warmerProvider.notifier).loadConfiguration();
    });
  }

  @override
  Widget build(BuildContext context) {
    // ignore: unused_local_variable - reserved for future i18n usage
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final themeExt = theme.extension<G777ThemeExtension>();
    final state = ref.watch(warmerProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(colorScheme),
          const SizedBox(height: 24),
          if (state.error != null) _buildErrorCard(colorScheme, state.error!),
          if (state.successMessage != null)
            _buildSuccessCard(colorScheme, state.successMessage!),
          const SizedBox(height: 16),
          _buildConfigCard(colorScheme, themeExt, state),
          const SizedBox(height: 24),
          _buildBotSelectionCard(colorScheme, themeExt, state),
          const SizedBox(height: 24),
          _buildActionButtons(colorScheme, state),
        ],
      ),
    );
  }

  Widget _buildHeader(ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'ACCOUNT WARMER',
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            letterSpacing: 2,
            fontFamily: 'Oxanium',
            color: colorScheme.primary,
            shadows: [
              Shadow(
                color: colorScheme.primary.withValues(alpha: 0.5),
                blurRadius: 15,
              ),
            ],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Configure automated warming to maintain account health and avoid rate limits.',
          style: TextStyle(
            color: colorScheme.onSurfaceVariant,
            fontSize: 12,
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }

  Widget _buildErrorCard(ColorScheme colorScheme, String error) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.statusError.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: colorScheme.statusError.withValues(alpha: 0.3),
        ),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: colorScheme.statusError),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              error,
              style: TextStyle(color: colorScheme.statusError),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 18),
            onPressed: () => ref.read(warmerProvider.notifier).clearError(),
          ),
        ],
      ),
    );
  }

  Widget _buildSuccessCard(ColorScheme colorScheme, String message) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.statusOnline.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: colorScheme.statusOnline.withValues(alpha: 0.3),
        ),
      ),
      child: Row(
        children: [
          Icon(Icons.check_circle_outline, color: colorScheme.statusOnline),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: TextStyle(color: colorScheme.statusOnline),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 18),
            onPressed: () =>
                ref.read(warmerProvider.notifier).clearSuccessMessage(),
          ),
        ],
      ),
    );
  }

  Widget _buildConfigCard(
    ColorScheme colorScheme,
    G777ThemeExtension? themeExt,
    WarmerState state,
  ) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(themeExt?.edgeRadius ?? 16),
        border: Border.all(color: colorScheme.primary.withValues(alpha: 0.3)),
        boxShadow: [
          BoxShadow(
            color: (themeExt?.glowColor ?? colorScheme.primary).withValues(
              alpha: themeExt?.glowIntensity ?? 0.05,
            ),
            blurRadius: themeExt?.glassBlur ?? 10,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'WARMER CONFIGURATION',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                  color: colorScheme.primary,
                ),
              ),
              _buildStatusToggle(colorScheme, state),
            ],
          ),
          const SizedBox(height: 24),
          _buildSlider(
            label: 'DAILY MESSAGE LIMIT',
            value: state.dailyLimit.toDouble(),
            displayValue: '${state.dailyLimit} msgs/day',
            min: 10,
            max: 500,
            divisions: 49,
            colorScheme: colorScheme,
            onChanged: (v) =>
                ref.read(warmerProvider.notifier).setDailyLimit(v.toInt()),
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: _buildSlider(
                  label: 'DELAY MIN (seconds)',
                  value: state.delayMin.toDouble(),
                  displayValue: '${state.delayMin}s',
                  min: 5,
                  max: 300,
                  divisions: 59,
                  colorScheme: colorScheme,
                  onChanged: (v) => ref
                      .read(warmerProvider.notifier)
                      .setDelayRange(v.toInt(), state.delayMax),
                ),
              ),
              const SizedBox(width: 32),
              Expanded(
                child: _buildSlider(
                  label: 'DELAY MAX (seconds)',
                  value: state.delayMax.toDouble(),
                  displayValue: '${state.delayMax}s',
                  min: 10,
                  max: 600,
                  divisions: 59,
                  colorScheme: colorScheme,
                  onChanged: (v) => ref
                      .read(warmerProvider.notifier)
                      .setDelayRange(state.delayMin, v.toInt()),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatusToggle(ColorScheme colorScheme, WarmerState state) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: state.isActive
            ? colorScheme.statusOnline.withValues(alpha: 0.1)
            : colorScheme.statusError.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: state.isActive
              ? colorScheme.statusOnline
              : colorScheme.statusError,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: state.isActive
                  ? colorScheme.statusOnline
                  : colorScheme.statusError,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            state.isActive ? 'ACTIVE' : 'INACTIVE',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: state.isActive
                  ? colorScheme.statusOnline
                  : colorScheme.statusError,
            ),
          ),
          const SizedBox(width: 8),
          Switch(
            value: state.isActive,
            onChanged: (_) => ref.read(warmerProvider.notifier).toggleActive(),
            activeThumbColor: colorScheme.statusOnline,
            inactiveThumbColor: colorScheme.statusError,
          ),
        ],
      ),
    );
  }

  Widget _buildSlider({
    required String label,
    required double value,
    required String displayValue,
    required double min,
    required double max,
    required int divisions,
    required ColorScheme colorScheme,
    required ValueChanged<double> onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
                color: colorScheme.onSurfaceVariant,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                displayValue,
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w900,
                  color: colorScheme.primary,
                  fontFamily: 'monospace',
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            trackHeight: 2,
            thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
            overlayShape: const RoundSliderOverlayShape(overlayRadius: 14),
          ),
          child: Slider(
            value: value,
            min: min,
            max: max,
            divisions: divisions,
            activeColor: colorScheme.primary,
            inactiveColor: colorScheme.outline.withValues(alpha: 0.3),
            onChanged: onChanged,
          ),
        ),
      ],
    );
  }

  Widget _buildBotSelectionCard(
    ColorScheme colorScheme,
    G777ThemeExtension? themeExt,
    WarmerState state,
  ) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(themeExt?.edgeRadius ?? 16),
        border: Border.all(color: colorScheme.outline.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'SELECT BOT INSTANCES',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                  color: colorScheme.primary,
                ),
              ),
              Row(
                children: [
                  TextButton(
                    onPressed: () =>
                        ref.read(warmerProvider.notifier).selectAllBots(),
                    child: Text(
                      'Select All',
                      style: TextStyle(
                        fontSize: 10,
                        color: colorScheme.primary,
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: () =>
                        ref.read(warmerProvider.notifier).deselectAllBots(),
                    child: Text(
                      'Clear',
                      style: TextStyle(
                        fontSize: 10,
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (state.availableBots.isEmpty)
            Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text(
                  'No bot instances available',
                  style: TextStyle(
                    color: colorScheme.onSurfaceVariant,
                    fontSize: 12,
                  ),
                ),
              ),
            )
          else
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: state.availableBots.map((botId) {
                final isSelected = state.selectedBots.contains(botId);
                return FilterChip(
                  label: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.smart_toy,
                        size: 14,
                        color: isSelected
                            ? colorScheme.onPrimary
                            : colorScheme.onSurfaceVariant,
                      ),
                      const SizedBox(width: 6),
                      Text(botId),
                    ],
                  ),
                  selected: isSelected,
                  onSelected: (_) =>
                      ref.read(warmerProvider.notifier).toggleBot(botId),
                  selectedColor: colorScheme.primary,
                  checkmarkColor: colorScheme.onPrimary,
                  backgroundColor: colorScheme.surfaceContainerHighest,
                  labelStyle: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: isSelected
                        ? colorScheme.onPrimary
                        : colorScheme.onSurface,
                  ),
                );
              }).toList(),
            ),
          const SizedBox(height: 16),
          Text(
            '${state.selectedBots.length} of ${state.availableBots.length} bots selected',
            style: TextStyle(fontSize: 11, color: colorScheme.onSurfaceVariant),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButtons(ColorScheme colorScheme, WarmerState state) {
    return Row(
      children: [
        Expanded(
          child: SizedBox(
            height: 54,
            child: ElevatedButton.icon(
              onPressed: state.isLoading
                  ? null
                  : () => ref.read(warmerProvider.notifier).saveConfiguration(),
              icon: state.isLoading
                  ? SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: colorScheme.onPrimary,
                      ),
                    )
                  : const Icon(Icons.save, size: 20),
              label: Text(
                state.isLoading ? 'SAVING...' : 'SAVE CONFIGURATION',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                  fontFamily: 'Oxanium',
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: colorScheme.primary,
                foregroundColor: colorScheme.onPrimary,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

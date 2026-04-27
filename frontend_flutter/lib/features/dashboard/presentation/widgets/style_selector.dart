import 'package:g777_client/core/theme/semantic_colors.dart';
import 'package:flutter/material.dart';
import 'package:g777_client/core/theme/theme_controller.dart';
import 'package:g777_client/l10n/app_localizations.dart';

class StyleSelector extends StatelessWidget {
  final ThemeController controller;
  final ThemeStyle currentStyle;

  const StyleSelector({
    super.key,
    required this.controller,
    required this.currentStyle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: colors.surfaceContainer,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: colors.outline.withValues(alpha: 0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l10n.visualEngine,
            style: const TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 16),
          _StyleButton(
            label: l10n.neonPink,
            style: ThemeStyle.neon,
            isSelected: currentStyle == ThemeStyle.neon,
            onScale: () => controller.setThemeStyle(ThemeStyle.neon),
            color: colors.styleNeon,
          ),
          const SizedBox(height: 8),
          _StyleButton(
            label: l10n.cyberBlue,
            style: ThemeStyle.professional,
            isSelected: currentStyle == ThemeStyle.professional,
            onScale: () => controller.setThemeStyle(ThemeStyle.professional),
            color: colors.styleProfessional,
          ),
          const SizedBox(height: 8),
          _StyleButton(
            label: l10n.industrial,
            style: ThemeStyle.industrial,
            isSelected: currentStyle == ThemeStyle.industrial,
            onScale: () => controller.setThemeStyle(ThemeStyle.industrial),
            color: colors.styleIndustrial,
          ),
          const SizedBox(height: 8),
          _StyleButton(
            label: 'Modern Glass', // Add missing label if not in l10n
            style: ThemeStyle.modernGlass,
            isSelected: currentStyle == ThemeStyle.modernGlass,
            onScale: () => controller.setThemeStyle(ThemeStyle.modernGlass),
            color: colors.primary,
          ),
        ],
      ),
    );
  }
}

class _StyleButton extends StatelessWidget {
  final String label;
  final ThemeStyle style;
  final bool isSelected;
  final VoidCallback onScale;
  final Color color;

  const _StyleButton({
    required this.label,
    required this.style,
    required this.isSelected,
    required this.onScale,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    return InkWell(
      onTap: onScale,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? color.withValues(alpha: 0.1) : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected
                ? color
                : colors.outline.withValues(alpha: colors.brightness == Brightness.dark ? 0.12 : 0.2),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Flexible(
              child: Text(
                label,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: isSelected
                      ? color
                      : colors.onSurface.withValues(alpha: colors.brightness == Brightness.dark ? 0.6 : 0.7),
                ),
                overflow: TextOverflow.ellipsis,
                maxLines: 1,
              ),
            ),
            if (isSelected)
              Padding(
                padding: const EdgeInsets.only(left: 4),
                child: Icon(Icons.check_circle_rounded, size: 14, color: color),
              ),
          ],
        ),
      ),
    );
  }
}

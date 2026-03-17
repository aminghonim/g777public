import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:g777_client/core/theme/theme_extensions.dart';
import 'package:g777_client/shared/providers/locale_provider.dart';
import 'package:g777_client/l10n/app_localizations.dart';

class GlobalNavbar extends ConsumerWidget implements PreferredSizeWidget {
  const GlobalNavbar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final locale = ref.watch(localeProvider);
    final l10n = AppLocalizations.of(context)!;

    return Container(
      height: 70,
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF0F0F23) : theme.cardColor,
        border: Border(
          bottom: BorderSide(
            color: theme.colorScheme.primary.withValues(alpha: 0.1),
            width: 1,
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Flexible(
            child: _buildLanguageToggle(ref, locale, theme, l10n, context),
          ),
          _buildSystemStatus(theme, l10n),
        ],
      ),
    );
  }

  Widget _buildLanguageToggle(
    WidgetRef ref,
    Locale locale,
    ThemeData theme,
    AppLocalizations l10n,
    BuildContext context,
  ) {
    return InkWell(
      onTap: () {
        ref.read(localeProvider.notifier).toggleLocale();
        final currentLocale = ref.read(localeProvider).languageCode;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.swapLanguageToast(currentLocale.toUpperCase())),
            backgroundColor: theme.colorScheme.primary,
            duration: const Duration(milliseconds: 800),
          ),
        );
      },
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          border: Border.all(
            color: theme.colorScheme.primary.withValues(alpha: 0.2),
          ),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.language, size: 14, color: theme.colorScheme.primary),
            const SizedBox(width: 4),
            Text(
              locale.languageCode.toUpperCase(),
              style: TextStyle(
                fontSize: 9,
                fontWeight: FontWeight.bold,
                fontFamily: 'Oxanium',
                color: theme.colorScheme.onSurface,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSystemStatus(ThemeData theme, AppLocalizations l10n) {
    return Padding(
      padding: const EdgeInsets.only(right: 12, left: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: const BoxDecoration(
              color: Color(0xFF00FF41),
              shape: BoxShape.circle,
              boxShadow: [BoxShadow(color: Color(0xFF00FF41), blurRadius: 4)],
            ),
          ),
          const SizedBox(width: 6),
          Text(
            l10n.live.toUpperCase(),
            style: TextStyle(
              color: theme.colorScheme.onSurface.withValues(alpha: 0.4),
              fontSize: 9,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(70);
}

class NavHexPainter extends CustomPainter {
  final Color color;
  final bool isActive;
  final G777ThemeExtension themeExt;

  NavHexPainter({
    required this.color,
    required this.isActive,
    required this.themeExt,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    final double slant = themeExt.cutCornerSize > 0
        ? themeExt.cutCornerSize
        : 12.0;
    final double glowIntensity = themeExt.glowIntensity;

    Path createPath(double inset) {
      final path = Path();
      final double x0 = inset;
      final double y0 = inset;
      final double xW = w - inset;
      final double yH = h - inset;

      path.moveTo(x0 + slant, y0);
      path.lineTo(xW, y0);
      path.lineTo(xW, yH - slant);
      path.lineTo(xW - slant, yH);
      path.lineTo(x0, yH);
      path.lineTo(x0, y0 + slant);
      path.close();
      return path;
    }

    final mainPath = createPath(0);
    final innerPath = createPath(2.5);

    if (isActive && glowIntensity > 0) {
      canvas.drawPath(
        mainPath,
        Paint()
          ..color = color.withValues(alpha: 0.3)
          ..maskFilter = MaskFilter.blur(BlurStyle.normal, glowIntensity / 1.5),
      );
    }

    canvas.drawPath(
      mainPath,
      Paint()
        ..color = color.withValues(alpha: isActive ? 0.12 : 0.03)
        ..style = PaintingStyle.fill,
    );

    canvas.drawPath(
      mainPath,
      Paint()
        ..color = color.withValues(alpha: isActive ? 1.0 : 0.25)
        ..style = PaintingStyle.stroke
        ..strokeWidth = isActive ? 1.5 : 1.0,
    );

    if (isActive) {
      canvas.drawPath(
        innerPath,
        Paint()
          ..color = color.withValues(alpha: 0.5)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 0.8,
      );

      final Paint accentPaint = Paint()..color = color;
      canvas.drawCircle(Offset(slant, 0), 1.2, accentPaint);
      canvas.drawCircle(Offset(w - slant, h), 1.2, accentPaint);
    }
  }

  @override
  bool shouldRepaint(covariant NavHexPainter oldDelegate) =>
      oldDelegate.isActive != isActive ||
      oldDelegate.color != color ||
      oldDelegate.themeExt != themeExt;
}

import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../../core/theme/app_theme.dart';

class AppBeveledRectangleBorder extends OutlinedBorder {
  final double bevelSize;
  final BorderRadius borderRadius;

  const AppBeveledRectangleBorder({
    super.side = BorderSide.none,
    this.bevelSize = 16.0,
    this.borderRadius = BorderRadius.zero,
  });

  @override
  EdgeInsetsGeometry get dimensions => EdgeInsets.all(side.width);

  @override
  Path getInnerPath(Rect rect, {TextDirection? textDirection}) {
    return _getPath(rect.deflate(side.width));
  }

  @override
  Path getOuterPath(Rect rect, {TextDirection? textDirection}) {
    return _getPath(rect);
  }

  Path _getPath(Rect rect) {
    final path = Path();
    final r = borderRadius.resolve(TextDirection.ltr);
    final b = bevelSize;

    path.moveTo(rect.left + r.topLeft.x + b, rect.top);
    path.lineTo(rect.right - r.topRight.x - b, rect.top);
    path.lineTo(rect.right - r.topRight.x, rect.top + b);
    path.lineTo(rect.right, rect.top + r.topRight.y + b);
    path.lineTo(rect.right, rect.bottom - r.bottomRight.y - b);
    path.lineTo(rect.right - r.bottomRight.x - b, rect.bottom);
    path.lineTo(rect.left + r.bottomLeft.x + b, rect.bottom);
    path.lineTo(rect.left, rect.bottom - r.bottomLeft.y - b);
    path.lineTo(rect.left, rect.top + r.topLeft.y + b);
    path.lineTo(rect.left + r.topLeft.x, rect.top + b);
    path.close();

    return path;
  }

  @override
  void paint(Canvas canvas, Rect rect, {TextDirection? textDirection}) {
    if (side.style == BorderStyle.none) return;

    final path = _getPath(rect);

    final glowPaint = Paint()
      ..color = side.color.withValues(alpha: 0.4)
      ..maskFilter = const MaskFilter.blur(BlurStyle.outer, 12)
      ..style = PaintingStyle.stroke
      ..strokeWidth = side.width + 6;

    final innerGlowPaint = Paint()
      ..color = side.color.withValues(alpha: 0.2)
      ..maskFilter = const MaskFilter.blur(BlurStyle.inner, 8)
      ..style = PaintingStyle.stroke
      ..strokeWidth = side.width + 2;

    final borderPaint = side.toPaint();

    canvas.drawPath(path, glowPaint);
    canvas.drawPath(path, innerGlowPaint);
    canvas.drawPath(path, borderPaint);
  }

  @override
  ShapeBorder scale(double t) {
    return AppBeveledRectangleBorder(
      side: side.scale(t),
      bevelSize: bevelSize * t,
      borderRadius: borderRadius * t,
    );
  }

  @override
  OutlinedBorder copyWith({BorderSide? side}) {
    return AppBeveledRectangleBorder(
      side: side ?? this.side,
      bevelSize: bevelSize,
      borderRadius: borderRadius,
    );
  }
}

class HexagonBorder extends ShapeBorder {
  final BorderSide side;
  final double rotation;
  final bool isActive;

  const HexagonBorder({
    this.side = BorderSide.none,
    this.rotation = 0,
    this.isActive = false,
  });

  @override
  EdgeInsetsGeometry get dimensions =>
      EdgeInsets.all(side.width + (isActive ? 4 : 0));

  @override
  Path getInnerPath(Rect rect, {TextDirection? textDirection}) {
    return _getPath(rect.deflate(side.width));
  }

  @override
  Path getOuterPath(Rect rect, {TextDirection? textDirection}) {
    return _getPath(rect);
  }

  Path _getPath(Rect rect) {
    final path = Path();
    final center = rect.center;
    final radius = math.min(rect.width, rect.height) / 2;

    for (int i = 0; i < 6; i++) {
      final angle = (i * 60 + rotation - 30) * math.pi / 180;
      final x = center.dx + radius * math.cos(angle);
      final y = center.dy + radius * math.sin(angle);

      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    path.close();
    return path;
  }

  @override
  void paint(Canvas canvas, Rect rect, {TextDirection? textDirection}) {
    if (side.style == BorderStyle.none) return;

    final path = _getPath(rect);

    if (isActive) {
      final glowPaint = Paint()
        ..color = side.color.withValues(alpha: 0.6)
        ..maskFilter = const MaskFilter.blur(BlurStyle.outer, 15)
        ..style = PaintingStyle.stroke
        ..strokeWidth = side.width + 8;

      canvas.drawPath(path, glowPaint);
    }

    final standardGlow = Paint()
      ..color = side.color.withValues(alpha: 0.3)
      ..maskFilter = const MaskFilter.blur(BlurStyle.outer, 8)
      ..style = PaintingStyle.stroke
      ..strokeWidth = side.width + 4;

    canvas.drawPath(path, standardGlow);
    canvas.drawPath(path, side.toPaint());
  }

  @override
  ShapeBorder scale(double t) {
    return HexagonBorder(
      side: side.scale(t),
      rotation: rotation,
      isActive: isActive,
    );
  }
}

class CircuitBackgroundPainter extends CustomPainter {
  final bool isDark;

  CircuitBackgroundPainter({this.isDark = true});

  @override
  void paint(Canvas canvas, Size size) {
    final baseColor = isDark ? AppColors.neonCyan : AppColors.neonCyanDark;

    final paint = Paint()
      ..color = baseColor.withValues(alpha: isDark ? 0.03 : 0.05)
      ..strokeWidth = 1
      ..style = PaintingStyle.stroke;

    const spacing = 80.0;

    for (double y = 0; y < size.height; y += spacing) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }

    for (double x = 0; x < size.width; x += spacing * 4) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) =>
      oldDelegate is CircuitBackgroundPainter && oldDelegate.isDark != isDark;
}

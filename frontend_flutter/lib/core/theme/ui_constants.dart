import 'package:flutter/material.dart';
import 'dart:math' as math;

class AppColors {
  static const Color backgroundPrimary = Color(0xFF070B1F);
  static const Color backgroundSecondary = Color(0xFF0A132D);
  static const Color backgroundCard = Color(0xFF0D1B3A);
  static const Color backgroundDark = Color(0xFF050818);

  // Neons
  static const Color neonCyan = Color(0xFF5BCFE8);
  static const Color neonCyanBright = Color(0xFF88E5F0);
  static const Color neonOrange = Color(0xFFFF9F43);
  static const Color neonPurple = Color(0xFFA259D1);

  // Text
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFF88E5F0);
  static const Color textMuted = Color(0xFF5A7A8A);
}

// 1. Beveled Card Shape
class AppBeveledRectangleBorder extends ShapeBorder {
  final BorderSide side;
  final double bevelSize;

  const AppBeveledRectangleBorder({
    this.side = BorderSide.none,
    this.bevelSize = 12.0,
  });

  @override
  EdgeInsetsGeometry get dimensions => EdgeInsets.all(side.width);

  @override
  Path getInnerPath(Rect rect, {TextDirection? textDirection}) =>
      _getPath(rect.deflate(side.width));

  @override
  Path getOuterPath(Rect rect, {TextDirection? textDirection}) =>
      _getPath(rect);

  Path _getPath(Rect rect) {
    return Path()
      ..moveTo(rect.left + bevelSize, rect.top)
      ..lineTo(rect.right - bevelSize, rect.top)
      ..lineTo(rect.right, rect.top + bevelSize)
      ..lineTo(rect.right, rect.bottom - bevelSize)
      ..lineTo(rect.right - bevelSize, rect.bottom)
      ..lineTo(rect.left + bevelSize, rect.bottom)
      ..lineTo(rect.left, rect.bottom - bevelSize)
      ..lineTo(rect.left, rect.top + bevelSize)
      ..close();
  }

  @override
  void paint(Canvas canvas, Rect rect, {TextDirection? textDirection}) {
    if (side.style == BorderStyle.none) return;
    final path = _getPath(rect);
    final paint = side.toPaint();
    // Glow Effect
    canvas.drawPath(
      path,
      Paint()
        ..color = side.color.withValues(alpha: 0.3)
        ..maskFilter = const MaskFilter.blur(BlurStyle.outer, 8)
        ..style = PaintingStyle.stroke
        ..strokeWidth = side.width + 4,
    );
    canvas.drawPath(path, paint);
  }

  @override
  ShapeBorder scale(double t) =>
      AppBeveledRectangleBorder(side: side.scale(t), bevelSize: bevelSize * t);
}

// 2. Hexagon Shape
class HexagonBorder extends ShapeBorder {
  final BorderSide side;
  final bool isActive;
  const HexagonBorder({this.side = BorderSide.none, this.isActive = false});

  @override
  EdgeInsetsGeometry get dimensions => EdgeInsets.all(side.width);

  @override
  Path getInnerPath(Rect rect, {TextDirection? textDirection}) =>
      _getPath(rect.deflate(side.width));

  @override
  Path getOuterPath(Rect rect, {TextDirection? textDirection}) =>
      _getPath(rect);

  Path _getPath(Rect rect) {
    final path = Path();
    final center = rect.center;
    final radius = math.min(rect.width, rect.height) / 2;
    for (int i = 0; i < 6; i++) {
      final angle = (i * 60) * math.pi / 180;
      final x = center.dx + radius * math.cos(angle);
      final y = center.dy + radius * math.sin(angle);
      i == 0 ? path.moveTo(x, y) : path.lineTo(x, y);
    }
    path.close();
    return path;
  }

  @override
  void paint(Canvas canvas, Rect rect, {TextDirection? textDirection}) {
    if (side.style == BorderStyle.none) return;
    final path = _getPath(rect);
    // Glow
    canvas.drawPath(
      path,
      Paint()
        ..color = side.color.withValues(alpha: 0.4)
        ..maskFilter = const MaskFilter.blur(BlurStyle.outer, 6)
        ..style = PaintingStyle.stroke
        ..strokeWidth = side.width + 3,
    );
    canvas.drawPath(path, side.toPaint());
  }

  @override
  ShapeBorder scale(double t) => HexagonBorder(side: side.scale(t));
}

// 3. Circuit Background
class CircuitBackgroundPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.neonCyan.withValues(alpha: 0.05)
      ..style = PaintingStyle.stroke;
    const spacing = 60.0;
    for (double y = 0; y < size.height; y += spacing) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
      for (double x = 0; x < size.width; x += spacing * 2) {
        canvas.drawCircle(
          Offset(x, y),
          2,
          Paint()..color = AppColors.neonCyan.withValues(alpha: 0.1),
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

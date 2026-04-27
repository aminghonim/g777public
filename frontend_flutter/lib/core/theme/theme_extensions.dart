import 'package:flutter/material.dart';

/// G777 Custom Theme Extension
/// Provides additional visual properties not covered by Material 3 standard.
@immutable
class G777ThemeExtension extends ThemeExtension<G777ThemeExtension> {
  final double glassBlur;
  final double glassOpacity;
  final Color? glowColor;
  final double glowIntensity;
  final double cutCornerSize;
  final double edgeRadius;

  const G777ThemeExtension({
    required this.glassBlur,
    required this.glassOpacity,
    this.glowColor,
    required this.glowIntensity,
    required this.cutCornerSize,
    required this.edgeRadius,
  });

  @override
  G777ThemeExtension copyWith({
    double? glassBlur,
    double? glassOpacity,
    Color? glowColor,
    double? glowIntensity,
    double? cutCornerSize,
    double? edgeRadius,
  }) {
    return G777ThemeExtension(
      glassBlur: glassBlur ?? this.glassBlur,
      glassOpacity: glassOpacity ?? this.glassOpacity,
      glowColor: glowColor ?? this.glowColor,
      glowIntensity: glowIntensity ?? this.glowIntensity,
      cutCornerSize: cutCornerSize ?? this.cutCornerSize,
      edgeRadius: edgeRadius ?? this.edgeRadius,
    );
  }

  @override
  G777ThemeExtension lerp(
    covariant ThemeExtension<G777ThemeExtension>? other,
    double t,
  ) {
    if (other is! G777ThemeExtension) return this;
    return G777ThemeExtension(
      glassBlur: _lerpDouble(glassBlur, other.glassBlur, t),
      glassOpacity: _lerpDouble(glassOpacity, other.glassOpacity, t),
      glowColor: Color.lerp(glowColor, other.glowColor, t),
      glowIntensity: _lerpDouble(glowIntensity, other.glowIntensity, t),
      cutCornerSize: _lerpDouble(cutCornerSize, other.cutCornerSize, t),
      edgeRadius: _lerpDouble(edgeRadius, other.edgeRadius, t),
    );
  }

  double _lerpDouble(double a, double b, double t) {
    return a + (b - a) * t;
  }

  factory G777ThemeExtension.neon(Color primaryColor) {
    return G777ThemeExtension(
      glassBlur: 0.0,
      glassOpacity: 1.0,
      glowColor: primaryColor.withValues(alpha: 0.6),
      glowIntensity: 10.0,
      cutCornerSize: 18.0,
      edgeRadius: 8.0,
    );
  }

  factory G777ThemeExtension.professional() {
    return const G777ThemeExtension(
      glassBlur: 0.0,
      glassOpacity: 1.0,
      glowColor: null,
      glowIntensity: 0.0,
      cutCornerSize: 0.0,
      edgeRadius: 12.0,
    );
  }

  factory G777ThemeExtension.industrial() {
    return const G777ThemeExtension(
      glassBlur: 0.0,
      glassOpacity: 1.0,
      glowColor: null,
      glowIntensity: 0.0,
      cutCornerSize: 12.0,
      edgeRadius: 2.0,
    );
  }

  factory G777ThemeExtension.modernGlass() {
    return const G777ThemeExtension(
      glassBlur: 15.0,
      glassOpacity: 0.8,
      glowColor: null,
      glowIntensity: 5.0,
      cutCornerSize: 16.0,
      edgeRadius: 16.0,
    );
  }
}

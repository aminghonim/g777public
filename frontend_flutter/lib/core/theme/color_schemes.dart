import 'package:flutter/material.dart';

/// G777 Refined Color Schemes (Master Tonal Palettes)
/// Derived from Material 3 Tonal Mapping algorithm.
class G777ColorSchemes {
  // Master Seed Colors (Updated based on Design System)
  static const Color _neonSeed = Color(0xFF7C3AED); // AI Purple
  static const Color _professionalSeed = Color(0xFF1A73E8);
  static const Color _industrialSeed = Color(0xFFF4511E);
  static const Color _modernGlassSeed = Color(0xFF7C3AED);

  /// 1. NEON STYLE
  static final ColorScheme neonLight = ColorScheme.fromSeed(
    seedColor: _neonSeed,
    brightness: Brightness.light,
    primary: const Color(0xFF9333EA), // Bold Purple
    onPrimary: Colors.white,
    surface: const Color(0xFFFAFAFA), // Crisp White
    onSurface: const Color(0xFF1E1B4B), // Deep Indigo Text
    surfaceContainer: const Color(0xFFF3F4F6),
  );

  static final ColorScheme neonDark = ColorScheme.fromSeed(
    seedColor: _neonSeed,
    brightness: Brightness.dark,
    primary: const Color(0xFFD946EF), // Fuchsia / Neon Magenta
    onPrimary: Colors.white,
    surface: const Color(0xFF050505), // OLED Black
    onSurface: const Color(0xFFF5F3FF),
    surfaceContainer: const Color(0xFF121212),
    secondary: const Color(0xFF22D3EE), // Cyan accent
  );

  /// 2. PROFESSIONAL STYLE
  static final ColorScheme professionalLight = ColorScheme.fromSeed(
    seedColor: _professionalSeed,
    brightness: Brightness.light,
    primary: const Color(0xFF2563EB), // Professional Blue
    surface: const Color(0xFFFFFFFF),
    onSurface: const Color(0xFF0F172A), // Deep Slate Text
    surfaceContainer: const Color(0xFFF8FAFC),
  );

  static final ColorScheme professionalDark = ColorScheme.fromSeed(
    seedColor: _professionalSeed,
    brightness: Brightness.dark,
    primary: const Color(0xFF3B82F6),
    surface: const Color(0xFF020617), // Deep Night Navy
    onSurface: const Color(0xFFF1F5F9),
    surfaceContainer: const Color(0xFF1E293B),
  );

  /// 3. INDUSTRIAL STYLE
  static final ColorScheme industrialLight = ColorScheme.fromSeed(
    seedColor: _industrialSeed,
    brightness: Brightness.light,
    primary: const Color(0xFFEA580C), // Sharp Orange
    surface: const Color(0xFFF5F5F4), // Light Stone
    onSurface: const Color(0xFF1C1917), // Deep Stone Text
    surfaceContainer: const Color(0xFFE7E5E4),
  );

  static final ColorScheme industrialDark = ColorScheme.fromSeed(
    seedColor: _industrialSeed,
    brightness: Brightness.dark,
    primary: const Color(0xFFF97316), // Safety Orange
    surface: const Color(0xFF1C1917), // Stone/Metal Grey
    onSurface: const Color(0xFFFAFAF9),
    surfaceContainer: const Color(0xFF292524),
    outline: const Color(0xFF44403C),
  );

  /// 4. MODERN/GLASS STYLE
  static final ColorScheme modernGlassLight = ColorScheme.fromSeed(
    seedColor: _modernGlassSeed,
    brightness: Brightness.light,
    primary: const Color(0xFF4F46E5), // Indigo
    surface: const Color(0xFFF1F5F9), // Very Light Slate
    onSurface: const Color(0xFF0F172A),
    surfaceContainer: const Color(0xFFE2E8F0).withValues(alpha: 0.6),
  );

  static final ColorScheme modernGlassDark = ColorScheme.fromSeed(
    seedColor: _modernGlassSeed,
    brightness: Brightness.dark,
    primary: const Color(0xFF7C3AED),
    surface: const Color(0xFF0F172A), // Deep glass-slate
    onSurface: const Color(0xFFE2E8F0),
    surfaceContainer: const Color(
      0xFF1E293B,
    ).withValues(alpha: 0.8), // Glass opacity
  );
}

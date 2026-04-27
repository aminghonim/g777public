import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'color_schemes.dart';
import 'theme_extensions.dart';

// =============================================================================
// LEGACY THEME SYSTEM (Preserved for compatibility)
// =============================================================================
class AppColors {
  static const Color darkBackgroundPrimary = Color(0xFF050A15);
  static const Color darkBackgroundSecondary = Color(0xFF0A132D);
  static const Color darkBackgroundCard = Color(0xFF0D1B3A);
  static const Color darkBackgroundDark = Color(0xFF050818);
  static const Color lightBackgroundPrimary = Color(0xFFE2E8F0);
  static const Color lightBackgroundSecondary = Color(0xFFCBD5E1);
  static const Color lightBackgroundCard = Color(0xFFF1F5F9);
  static const Color lightBackgroundDark = Color(0xFF94A3B8);
  static const Color neonCyan = Color(0xFF5AD1E7);
  static const Color neonCyanBright = Color(0xFF7CEDF6);
  static const Color neonCyanDark = Color(0xFF2A8A9C);
  static const Color neonOrange = Color(0xFFFF9F43);
  static const Color neonOrangeBright = Color(0xFFFFB347);
  static const Color neonOrangeDark = Color(0xFFD38E4F);
  static const Color neonPurple = Color(0xFFA259D1);
  static const Color neonPurpleBright = Color(0xFFBF7CE8);
  static const Color neonPurpleDark = Color(0xFF6B2D9C);
  static const Color darkTextPrimary = Color(0xFFFFFFFF);
  static const Color darkTextSecondary = Color(0xFF88E5F0);
  static const Color darkTextMuted = Color(0xFF5A7A8A);
  static const Color lightTextPrimary = Color(0xFF0F172A);
  static const Color lightTextSecondary = Color(0xFF475569);
  static const Color lightTextMuted = Color(0xFF94A3B8);
}

class ThemeColors {
  final Color backgroundPrimary;
  final Color backgroundSecondary;
  final Color backgroundCard;
  final Color backgroundDark;
  final Color textPrimary;
  final Color textSecondary;
  final Color textMuted;
  final bool isDark;

  const ThemeColors({
    required this.backgroundPrimary,
    required this.backgroundSecondary,
    required this.backgroundCard,
    required this.backgroundDark,
    required this.textPrimary,
    required this.textSecondary,
    required this.textMuted,
    required this.isDark,
  });

  static const ThemeColors dark = ThemeColors(
    backgroundPrimary: AppColors.darkBackgroundPrimary,
    backgroundSecondary: AppColors.darkBackgroundSecondary,
    backgroundCard: AppColors.darkBackgroundCard,
    backgroundDark: AppColors.darkBackgroundDark,
    textPrimary: AppColors.darkTextPrimary,
    textSecondary: AppColors.darkTextSecondary,
    textMuted: AppColors.darkTextMuted,
    isDark: true,
  );

  static const ThemeColors light = ThemeColors(
    backgroundPrimary: AppColors.lightBackgroundPrimary,
    backgroundSecondary: AppColors.lightBackgroundSecondary,
    backgroundCard: AppColors.lightBackgroundCard,
    backgroundDark: AppColors.lightBackgroundDark,
    textPrimary: AppColors.lightTextPrimary,
    textSecondary: AppColors.lightTextSecondary,
    textMuted: AppColors.lightTextMuted,
    isDark: false,
  );
}

class AppTheme {
  static ThemeColors getThemeColors(bool isDark) {
    return isDark ? ThemeColors.dark : ThemeColors.light;
  }

  static ThemeData getTheme(bool isDark) {
    final colors = getThemeColors(isDark);

    return ThemeData(
      useMaterial3: true,
      brightness: isDark ? Brightness.dark : Brightness.light,
      scaffoldBackgroundColor: colors.backgroundPrimary,
      primaryColor: AppColors.neonCyan,
      colorScheme: ColorScheme(
        brightness: isDark ? Brightness.dark : Brightness.light,
        primary: AppColors.neonCyan,
        onPrimary: Colors.white,
        secondary: AppColors.neonOrange,
        onSecondary: Colors.white,
        tertiary: AppColors.neonPurple,
        onTertiary: Colors.white,
        error: Colors.redAccent,
        onError: Colors.white,
        surface: colors.backgroundCard,
        onSurface: colors.textPrimary,
      ),
      textTheme: TextTheme(
        displayLarge: TextStyle(
          color: colors.textPrimary,
          fontSize: 48,
          fontWeight: FontWeight.bold,
          letterSpacing: 4,
        ),
        titleLarge: TextStyle(
          color: colors.textPrimary,
          fontSize: 20,
          fontWeight: FontWeight.bold,
          letterSpacing: 2,
        ),
        bodyLarge: TextStyle(color: colors.textPrimary, fontSize: 16),
        bodyMedium: TextStyle(color: colors.textSecondary, fontSize: 14),
        labelSmall: TextStyle(color: colors.textMuted, fontSize: 12),
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: colors.backgroundSecondary,
        foregroundColor: colors.textPrimary,
        elevation: 0,
        systemOverlayStyle: isDark
            ? SystemUiOverlayStyle.light
            : SystemUiOverlayStyle.dark,
      ),
    );
  }
}

// =============================================================================
// MODERN G777 THEME SYSTEM (New Standard)
// =============================================================================

/// G777 Application Themes
/// Assembles complete ThemeData objects with custom button styles,
/// typography, and visual effects for each style variant.
class G777AppThemes {
  // Typography (Updated based on Design System)
  static const String _primaryFontFamily = 'Fira Sans';
  static const String _headingFontFamily = 'Fira Code';

  /// Base Text Theme (shared across all styles)
  static TextTheme _baseTextTheme(ColorScheme colorScheme) {
    return TextTheme(
      displayLarge: TextStyle(
        fontFamily: _headingFontFamily,
        fontSize: 57,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      displayMedium: TextStyle(
        fontFamily: _headingFontFamily,
        fontSize: 45,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      displaySmall: TextStyle(
        fontFamily: _headingFontFamily,
        fontSize: 36,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      headlineLarge: TextStyle(
        fontFamily: _headingFontFamily,
        fontSize: 32,
        fontWeight: FontWeight.w500,
        color: colorScheme.onSurface,
      ),
      headlineMedium: TextStyle(
        fontFamily: _headingFontFamily,
        fontSize: 28,
        fontWeight: FontWeight.w500,
        color: colorScheme.onSurface,
      ),
      headlineSmall: TextStyle(
        fontFamily: _headingFontFamily,
        fontSize: 24,
        fontWeight: FontWeight.w500,
        color: colorScheme.onSurface,
      ),
      bodyLarge: TextStyle(
        fontFamily: _primaryFontFamily,
        fontSize: 16,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      bodyMedium: TextStyle(
        fontFamily: _primaryFontFamily,
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      bodySmall: TextStyle(
        fontFamily: _primaryFontFamily,
        fontSize: 12,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurfaceVariant,
      ),
      labelLarge: TextStyle(
        fontFamily: _primaryFontFamily,
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: colorScheme.onPrimary,
      ),
    );
  }

  /// Build ThemeData with all components
  static ThemeData _buildTheme({
    required ColorScheme colorScheme,
    required G777ThemeExtension extension,
    required String fontFamily,
    required OutlinedBorder buttonShape,
    double elevation = 0,
  }) {
    final baseTextTheme = _baseTextTheme(colorScheme);

    // Dynamically fetch GoogleFont
    TextTheme googleTextTheme;
    try {
      googleTextTheme = baseTextTheme.apply(
        fontFamily: GoogleFonts.getFont(fontFamily).fontFamily,
      );
    } catch (e) {
      googleTextTheme = baseTextTheme.apply(fontFamily: fontFamily);
    }

    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: colorScheme.surface,
      colorScheme: colorScheme,
      fontFamily: googleTextTheme.bodyLarge?.fontFamily,
      textTheme: googleTextTheme,
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: colorScheme.primary,
          foregroundColor: colorScheme.onPrimary,
          elevation: elevation,
          shape: buttonShape,
          shadowColor: colorScheme.primary.withValues(alpha: 0.4),
        ),
      ),
      textButtonTheme: _textButtonTheme(colorScheme),
      extensions: [extension],
      cardTheme: CardThemeData(
        elevation: elevation / 2,
        shape: buttonShape,
        color: colorScheme.surfaceContainer,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: colorScheme.surface,
        foregroundColor: colorScheme.onSurface,
        elevation: 0,
        centerTitle: true,
      ),
    );
  }

  // ============================================================================
  // NEON THEMES
  // ============================================================================
  static ThemeData get neonDark => _buildTheme(
    colorScheme: G777ColorSchemes.neonDark,
    extension: G777ThemeExtension.neon(G777ColorSchemes.neonDark.primary),
    fontFamily: 'Oxanium', // Futuristic Cyberpunk Font
    buttonShape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(20),
    ),
    elevation: 10,
  );

  static ThemeData get neonLight => _buildTheme(
    colorScheme: G777ColorSchemes.neonLight,
    extension: G777ThemeExtension.neon(G777ColorSchemes.neonLight.primary),
    fontFamily: 'Oxanium',
    buttonShape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(20),
    ),
    elevation: 10,
  );

  // ============================================================================
  // PROFESSIONAL THEMES
  // ============================================================================
  static ThemeData get professionalDark => _buildTheme(
    colorScheme: G777ColorSchemes.professionalDark,
    extension: G777ThemeExtension.professional(),
    fontFamily: 'Fira Sans',
    buttonShape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
    ),
    elevation: 2,
  );

  static ThemeData get professionalLight => _buildTheme(
    colorScheme: G777ColorSchemes.professionalLight,
    extension: G777ThemeExtension.professional(),
    fontFamily: 'Fira Sans',
    buttonShape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(12),
    ),
    elevation: 2,
  );

  // ============================================================================
  // INDUSTRIAL THEMES
  // ============================================================================
  static ThemeData get industrialDark => _buildTheme(
    colorScheme: G777ColorSchemes.industrialDark,
    extension: G777ThemeExtension.industrial(),
    fontFamily: 'Roboto Mono', // Technical / Monospace Font
    buttonShape: BeveledRectangleBorder(borderRadius: BorderRadius.circular(6)),
    elevation: 0,
  );

  static ThemeData get industrialLight => _buildTheme(
    colorScheme: G777ColorSchemes.industrialLight,
    extension: G777ThemeExtension.industrial(),
    fontFamily: 'Roboto Mono',
    buttonShape: BeveledRectangleBorder(borderRadius: BorderRadius.circular(6)),
    elevation: 0,
  );

  // ============================================================================
  // MODERN/GLASS THEMES
  // ============================================================================
  static ThemeData get modernGlassDark => _buildTheme(
    colorScheme: G777ColorSchemes.modernGlassDark,
    extension: G777ThemeExtension.modernGlass(),
    fontFamily: 'Fira Sans',
    buttonShape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(16),
    ),
    elevation: 4,
  );

  static ThemeData get modernGlassLight => _buildTheme(
    colorScheme: G777ColorSchemes.modernGlassLight,
    extension: G777ThemeExtension.modernGlass(),
    fontFamily: 'Fira Sans',
    buttonShape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(16),
    ),
    elevation: 4,
  );

  static TextButtonThemeData _textButtonTheme(ColorScheme colorScheme) {
    return TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: colorScheme.primary,
        textStyle: const TextStyle(
          fontWeight: FontWeight.bold,
          letterSpacing: 1,
        ),
      ),
    );
  }
}

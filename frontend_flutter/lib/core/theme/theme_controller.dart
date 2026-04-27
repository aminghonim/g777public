import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:g777_client/core/theme/app_theme.dart';
import 'package:g777_client/shared/providers/theme_provider.dart';
import 'package:g777_client/core/providers/shared_prefs_provider.dart';

/// Theme Style Enum
enum ThemeStyle { neon, professional, industrial, modernGlass }

/// Theme Style Notifier (Riverpod 3 - Notifier)
class ThemeStyleNotifier extends Notifier<ThemeStyle> {
  static const String _key = 'app_theme_style';

  @override
  ThemeStyle build() {
    final prefs = ref.watch(sharedPreferencesProvider);
    return _getInitialStyle(prefs);
  }

  static ThemeStyle _getInitialStyle(SharedPreferences prefs) {
    final index = prefs.getInt(_key) ?? 0;
    if (index >= 0 && index < ThemeStyle.values.length) {
      return ThemeStyle.values[index];
    }
    return ThemeStyle.neon;
  }

  Future<void> setThemeStyle(ThemeStyle style) async {
    state = style;
    final prefs = ref.read(sharedPreferencesProvider);
    await prefs.setInt(_key, style.index);
  }
}

/// Theme Style Provider
final themeStyleProvider = NotifierProvider<ThemeStyleNotifier, ThemeStyle>(
  ThemeStyleNotifier.new,
);

/// Computed Theme Provider (Light)
final lightThemeProvider = Provider<ThemeData>((ref) {
  final style = ref.watch(themeStyleProvider);
  switch (style) {
    case ThemeStyle.neon:
      return G777AppThemes.neonLight;
    case ThemeStyle.professional:
      return G777AppThemes.professionalLight;
    case ThemeStyle.industrial:
      return G777AppThemes.industrialLight;
    case ThemeStyle.modernGlass:
      return G777AppThemes.modernGlassLight;
  }
});

/// Computed Theme Provider (Dark)
final darkThemeProvider = Provider<ThemeData>((ref) {
  final style = ref.watch(themeStyleProvider);
  switch (style) {
    case ThemeStyle.neon:
      return G777AppThemes.neonDark;
    case ThemeStyle.professional:
      return G777AppThemes.professionalDark;
    case ThemeStyle.industrial:
      return G777AppThemes.industrialDark;
    case ThemeStyle.modernGlass:
      return G777AppThemes.modernGlassDark;
  }
});

/// Theme Controller (for UI interactions)
class ThemeController {
  final WidgetRef ref;

  ThemeController(this.ref);

  void toggleThemeMode() {
    ref.read(themeModeProvider.notifier).toggleTheme();
  }

  void setThemeStyle(ThemeStyle style) {
    ref.read(themeStyleProvider.notifier).setThemeStyle(style);
  }

  ThemeMode get currentMode => ref.read(themeModeProvider).flutterThemeMode;
  ThemeStyle get currentStyle => ref.read(themeStyleProvider);
}

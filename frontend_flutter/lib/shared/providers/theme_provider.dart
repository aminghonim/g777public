import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:g777_client/core/providers/shared_prefs_provider.dart';

enum ThemeModeType { dark, light, system }

final themeModeProvider =
    StateNotifierProvider<ThemeModeNotifier, ThemeModeType>((ref) {
      final prefs = ref.watch(sharedPreferencesProvider);
      return ThemeModeNotifier(prefs);
    });

class ThemeModeNotifier extends StateNotifier<ThemeModeType> {
  final SharedPreferences prefs;

  ThemeModeNotifier(this.prefs) : super(_getInitialTheme(prefs));

  static const String _key = 'app_theme_mode';

  static ThemeModeType _getInitialTheme(SharedPreferences prefs) {
    final index = prefs.getInt(_key) ?? 0;
    if (index >= 0 && index < ThemeModeType.values.length) {
      return ThemeModeType.values[index];
    }
    return ThemeModeType.dark;
  }

  Future<void> setThemeMode(ThemeModeType mode) async {
    state = mode;
    await prefs.setInt(_key, mode.index);
  }

  Future<void> toggleTheme() async {
    final newMode = state == ThemeModeType.dark
        ? ThemeModeType.light
        : ThemeModeType.dark;
    await setThemeMode(newMode);
  }

  ThemeMode get flutterThemeMode {
    switch (state) {
      case ThemeModeType.dark:
        return ThemeMode.dark;
      case ThemeModeType.light:
        return ThemeMode.light;
      case ThemeModeType.system:
        return ThemeMode.system;
    }
  }
}

extension ThemeModeTypeX on ThemeModeType {
  ThemeMode get flutterThemeMode {
    switch (this) {
      case ThemeModeType.dark:
        return ThemeMode.dark;
      case ThemeModeType.light:
        return ThemeMode.light;
      case ThemeModeType.system:
        return ThemeMode.system;
    }
  }
}

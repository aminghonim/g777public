import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

final localeProvider = NotifierProvider<LocaleNotifier, Locale>(
  LocaleNotifier.new,
);

class LocaleNotifier extends Notifier<Locale> {
  static const String _key = 'app_locale';

  @override
  Locale build() {
    _loadLocale();
    return const Locale('ar');
  }

  Future<void> _loadLocale() async {
    final prefs = await SharedPreferences.getInstance();
    final code = prefs.getString(_key) ?? 'ar';
    state = Locale(code);
  }

  Future<void> toggleLocale() async {
    final newCode = state.languageCode == 'ar' ? 'en' : 'ar';
    state = Locale(newCode);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, newCode);
  }

  Future<void> setLocale(String languageCode) async {
    state = Locale(languageCode);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, languageCode);
  }
}

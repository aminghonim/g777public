import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Storage key constant for the sensitive API key
const String _kGlobalApiKey = 'g777_global_api_key';

// Settings State Model
class G777Settings {
  final String theme;
  final String language;
  final String evolutionApiUrl;
  final String globalApiKey;
  final int minDelay;
  final int maxDelay;
  final int dailyLimit;
  final String aiModel;
  final double aiCreativity;
  final String version;

  G777Settings({
    this.theme = 'Neon',
    this.language = 'ar',
    this.evolutionApiUrl = 'http://localhost:8080',
    this.globalApiKey = '',
    this.minDelay = 5,
    this.maxDelay = 15,
    this.dailyLimit = 500,
    this.aiModel = 'Gemini 2.0 Flash',
    this.aiCreativity = 0.7,
    this.version = '2.2.0',
  });

  G777Settings copyWith({
    String? theme,
    String? language,
    String? evolutionApiUrl,
    String? globalApiKey,
    int? minDelay,
    int? maxDelay,
    int? dailyLimit,
    String? aiModel,
    double? aiCreativity,
    String? version,
  }) {
    return G777Settings(
      theme: theme ?? this.theme,
      language: language ?? this.language,
      evolutionApiUrl: evolutionApiUrl ?? this.evolutionApiUrl,
      globalApiKey: globalApiKey ?? this.globalApiKey,
      minDelay: minDelay ?? this.minDelay,
      maxDelay: maxDelay ?? this.maxDelay,
      dailyLimit: dailyLimit ?? this.dailyLimit,
      aiModel: aiModel ?? this.aiModel,
      aiCreativity: aiCreativity ?? this.aiCreativity,
      version: version ?? this.version,
    );
  }
}

// Settings Notifier (Riverpod 3)
class SettingsNotifier extends Notifier<G777Settings> {
  // Hardware-backed encrypted storage for sensitive credentials
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage(
    wOptions: WindowsOptions(),
  );

  @override
  G777Settings build() {
    _init();
    return G777Settings();
  }

  Future<void> _init() async {
    final prefs = await SharedPreferences.getInstance();

    String apiKey = '';
    try {
      apiKey = await _secureStorage.read(key: _kGlobalApiKey) ?? '';
    } catch (e) {
      debugPrint('SecureStorage Read Error: $e');
    }

    state = G777Settings(
      theme: prefs.getString('theme') ?? 'Neon',
      language: prefs.getString('app_locale') ?? 'ar',
      evolutionApiUrl:
          prefs.getString('evolutionApiUrl') ?? 'http://localhost:8080',
      globalApiKey: apiKey,
      minDelay: prefs.getInt('minDelay') ?? 5,
      maxDelay: prefs.getInt('maxDelay') ?? 15,
      dailyLimit: prefs.getInt('dailyLimit') ?? 500,
      aiModel: prefs.getString('aiModel') ?? 'Gemini 2.0 Flash',
      aiCreativity: prefs.getDouble('aiCreativity') ?? 0.7,
      version: prefs.getString('system_version') ?? '2.2.0',
    );
  }

  Future<void> updateSettings(G777Settings newSettings) async {
    state = newSettings;

    try {
      await _secureStorage.write(
        key: _kGlobalApiKey,
        value: newSettings.globalApiKey,
      );
    } catch (e) {
      debugPrint('SecureStorage Write Error: $e');
    }

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('theme', newSettings.theme);
    await prefs.setString('app_locale', newSettings.language);
    await prefs.setString('evolutionApiUrl', newSettings.evolutionApiUrl);
    await prefs.setInt('minDelay', newSettings.minDelay);
    await prefs.setInt('maxDelay', newSettings.maxDelay);
    await prefs.setInt('dailyLimit', newSettings.dailyLimit);
    await prefs.setString('aiModel', newSettings.aiModel);
    await prefs.setDouble('aiCreativity', newSettings.aiCreativity);
  }
}

final settingsProvider = NotifierProvider<SettingsNotifier, G777Settings>(
  SettingsNotifier.new,
);

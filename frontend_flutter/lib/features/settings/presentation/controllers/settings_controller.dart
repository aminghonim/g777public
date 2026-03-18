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

// Settings Controller
class SettingsNotifier extends StateNotifier<G777Settings> {
  late SharedPreferences _prefs;

  // Hardware-backed encrypted storage for sensitive credentials
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage(
    wOptions: WindowsOptions(),
  );

  SettingsNotifier() : super(G777Settings()) {
    _init();
  }

  Future<void> _init() async {
    _prefs = await SharedPreferences.getInstance();

    // Read sensitive API key from secure storage with error handling
    String apiKey = '';
    try {
      apiKey = await _secureStorage.read(key: _kGlobalApiKey) ?? '';
    } catch (e) {
      debugPrint('SecureStorage Read Error: $e');
      // Access denied or corrupt data - proceed with empty key
      // Optionally try to clear storage if possible, but don't crash
    }

    state = G777Settings(
      theme: _prefs.getString('theme') ?? 'Neon',
      language: _prefs.getString('app_locale') ?? 'ar',
      evolutionApiUrl:
          _prefs.getString('evolutionApiUrl') ?? 'http://localhost:8080',
      globalApiKey: apiKey,
      minDelay: _prefs.getInt('minDelay') ?? 5,
      maxDelay: _prefs.getInt('maxDelay') ?? 15,
      dailyLimit: _prefs.getInt('dailyLimit') ?? 500,
      aiModel: _prefs.getString('aiModel') ?? 'Gemini 2.0 Flash',
      aiCreativity: _prefs.getDouble('aiCreativity') ?? 0.7,
      version: _prefs.getString('system_version') ?? '2.2.0',
    );
  }

  Future<void> updateSettings(G777Settings newSettings) async {
    state = newSettings;

    // Store sensitive API key in hardware-encrypted secure storage
    try {
      await _secureStorage.write(
        key: _kGlobalApiKey,
        value: newSettings.globalApiKey,
      );
    } catch (e) {
      debugPrint('SecureStorage Write Error: $e');
      // If write fails (locked file), we log it but don't crash the app
    }

    // Store non-sensitive settings in SharedPreferences
    await _prefs.setString('theme', newSettings.theme);
    await _prefs.setString('app_locale', newSettings.language);
    await _prefs.setString('evolutionApiUrl', newSettings.evolutionApiUrl);
    await _prefs.setInt('minDelay', newSettings.minDelay);
    await _prefs.setInt('maxDelay', newSettings.maxDelay);
    await _prefs.setInt('dailyLimit', newSettings.dailyLimit);
    await _prefs.setString('aiModel', newSettings.aiModel);
    await _prefs.setDouble('aiCreativity', newSettings.aiCreativity);
  }
}

final settingsProvider = StateNotifierProvider<SettingsNotifier, G777Settings>((
  ref,
) {
  return SettingsNotifier();
});

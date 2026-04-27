import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageService {
  // Use a singleton pattern for the secure storage instance
  static const FlutterSecureStorage _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(),
    wOptions: WindowsOptions(), // Uses Windows Data Protection API (DPAPI)
  );

  /// Saves a sensitive value securely.
  static Future<void> write(String key, String value) async {
    await _storage.write(key: key, value: value);
  }

  /// Reads a sensitive value securely.
  static Future<String?> read(String key) async {
    return await _storage.read(key: key);
  }

  /// Deletes a specific key.
  static Future<void> delete(String key) async {
    await _storage.delete(key: key);
  }

  /// Clears all stored data (Careful!).
  static Future<void> deleteAll() async {
    await _storage.deleteAll();
  }
}

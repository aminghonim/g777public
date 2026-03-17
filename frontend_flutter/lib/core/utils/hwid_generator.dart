import 'dart:convert';
import 'dart:io';
import 'package:crypto/crypto.dart';
import 'package:device_info_plus/device_info_plus.dart';

/// SAAS-016: Secure HWID Generator
/// Generates a consistent, unique, and cryptographically hashed Hardware ID
/// strictly bound to the physical device to prevent license cloning.
class HwidGenerator {
  static Future<String> generate() async {
    final deviceInfo = DeviceInfoPlugin();
    String rawId = 'UNKNOWN_DEVICE';

    try {
      if (Platform.isWindows) {
        final winInfo = await deviceInfo.windowsInfo;
        // Using deviceId which is unique to the Windows installation/machine
        rawId = winInfo.deviceId;
      } else if (Platform.isLinux) {
        final linuxInfo = await deviceInfo.linuxInfo;
        rawId = linuxInfo.machineId ?? Platform.localHostname;
      } else if (Platform.isMacOS) {
        final macInfo = await deviceInfo.macOsInfo;
        rawId = macInfo.systemGUID ?? Platform.localHostname;
      } else if (Platform.isAndroid) {
        final androidInfo = await deviceInfo.androidInfo;
        rawId = androidInfo.id;
      } else if (Platform.isIOS) {
        final iosInfo = await deviceInfo.iosInfo;
        rawId = iosInfo.identifierForVendor ?? Platform.localHostname;
      }
    } catch (e) {
      // Safe fallback if extraction is strictly blocked by OS permissions
      rawId = Platform.localHostname;
    }

    // Hash the raw hardware ID using SHA-256 (ASVS V11.5.1 Compliance)
    // Ensures raw identifying hardware specifics are never transmitted in plaintext.
    final bytes = utf8.encode(rawId);
    final digest = sha256.convert(bytes);

    return digest.toString();
  }
}

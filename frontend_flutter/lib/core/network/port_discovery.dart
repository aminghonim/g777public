import 'dart:convert';
import 'dart:developer' as dev;
import 'dart:io';
import 'package:path/path.dart' as p;

class PortDiscovery {
  static const String _sessionFile = 'secure_session.json';
  static const String _tempDir = '.antigravity';

  /// Discovers the active session (port and token) from the lock file.
  static Future<Map<String, dynamic>?> getActiveSession() async {
    try {
      final List<String> searchPaths = [
        p.join(Directory.current.path, _tempDir, _sessionFile),
        p.join(Directory.current.path, '..', _tempDir, _sessionFile),
        p.join(Directory.current.path, '../..', _tempDir, _sessionFile),
        // Fallback for Windows specific absolute path if necessary
        'D:\\WORK\\2\\.antigravity\\secure_session.json',
      ];

      for (String path in searchPaths) {
        final File lockFile = File(path);
        if (await lockFile.exists()) {
          final String content = await lockFile.readAsString();
          dev.log(
            '[PortDiscovery] Found session lock at: $path',
            name: 'G777.PortDiscovery',
          );
          return jsonDecode(content) as Map<String, dynamic>;
        }
      }

      dev.log(
        '[PortDiscovery] Session file NOT found in any search path.',
        name: 'G777.PortDiscovery',
      );
      return null;
    } catch (e) {
      dev.log(
        '[PortDiscovery] Error reading session: $e',
        name: 'G777.PortDiscovery',
      );
      return null;
    }
  }
}

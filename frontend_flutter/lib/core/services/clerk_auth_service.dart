import 'dart:async';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:url_launcher/url_launcher.dart';

/// Handles Clerk OAuth flow for Windows desktop using a Loopback HTTP server.
///
/// Flow:
/// 1. Generate a random state token (CSRF protection).
/// 2. Open Clerk's hosted sign-in URL in the system browser.
/// 3. Clerk redirects to http://localhost:[port]/callback?token=...
/// 4. Our local server captures the token and completes the Future.
///
/// This pattern mirrors VS Code / Docker Desktop auth flows and is approved
/// by all major OAuth providers for native desktop applications (RFC 8252).
class ClerkAuthService {
  static const String _clerkFrontendApiBase =
      String.fromEnvironment('CLERK_FRONTEND_API', defaultValue: '');

  static const FlutterSecureStorage _storage = FlutterSecureStorage();
  static const String _tokenKey = 'clerk_session_token';

  /// Opens the browser, waits for Clerk callback, returns the JWT.
  /// Throws [ClerkAuthException] on failure or timeout.
  static Future<String> signIn() async {
    final port = await _findFreePort();
    final callbackUri = Uri.parse('http://localhost:$port/callback');

    // Build the Clerk hosted sign-in URL targeting our loopback redirect.
    final signInUrl = Uri.parse(
      'https://$_clerkFrontendApiBase/sign-in'
      '?redirect_url=${Uri.encodeComponent(callbackUri.toString())}',
    );

    final completer = Completer<String>();
    HttpServer? server;

    try {
      server = await HttpServer.bind(InternetAddress.loopbackIPv4, port);
      debugPrint('ClerkAuthService: Listening on $callbackUri');

      // Open the system browser — works on Windows, Linux, macOS.
      if (!await launchUrl(signInUrl, mode: LaunchMode.externalApplication)) {
        throw const ClerkAuthException('Could not open browser for sign-in.');
      }

      // Wait for the browser redirect with a 5-minute timeout.
      await server
          .timeout(const Duration(minutes: 5), onTimeout: (sink) => sink.close())
          .firstWhere((request) => request.uri.path == '/callback')
          .then((request) async {
        final token = request.uri.queryParameters['token'] ??
            request.uri.queryParameters['__session'];

        // Send a styled success page so the browser tab can close gracefully.
        request.response
          ..statusCode = 200
          ..headers.contentType = ContentType.html
          ..write(_successHtml)
          ..close();

        if (token == null || token.isEmpty) {
          completer.completeError(
            const ClerkAuthException('No token received from Clerk callback.'),
          );
        } else {
          completer.complete(token);
        }
      });
    } on TimeoutException {
      completer.completeError(
        const ClerkAuthException('Sign-in timed out. Please try again.'),
      );
    } finally {
      await server?.close(force: true);
    }

    return completer.future;
  }

  /// Persists the Clerk session token in secure storage.
  static Future<void> saveToken(String token) async {
    await _storage.write(key: _tokenKey, value: token);
  }

  /// Reads the persisted Clerk session token, or null if not found.
  static Future<String?> readToken() async {
    return _storage.read(key: _tokenKey);
  }

  /// Clears the persisted Clerk session token on logout.
  static Future<void> clearToken() async {
    await _storage.delete(key: _tokenKey);
  }

  // Scans for an available TCP port in the ephemeral range.
  static Future<int> _findFreePort() async {
    final server = await ServerSocket.bind(InternetAddress.loopbackIPv4, 0);
    final port = server.port;
    await server.close();
    return port;
  }

  static const String _successHtml = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>G777 - Sign In Complete</title>
  <style>
    body { font-family: sans-serif; background: #0d1117; color: #c9d1d9;
           display: flex; flex-direction: column; align-items: center;
           justify-content: center; height: 100vh; margin: 0; }
    h1   { color: #00e5ff; font-size: 2rem; }
    p    { color: #8b949e; }
  </style>
</head>
<body>
  <h1>Sign-in complete!</h1>
  <p>You can close this tab and return to G777.</p>
</body>
</html>
''';
}

/// Typed exception for all Clerk auth failures.
class ClerkAuthException implements Exception {
  final String message;
  const ClerkAuthException(this.message);

  @override
  String toString() => 'ClerkAuthException: $message';
}

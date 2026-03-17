import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:g777_client/shared/widgets/hex_sidebar.dart';
import 'package:go_router/go_router.dart';

void main() {
  setUpAll(() {
    FlutterSecureStorage.setMockInitialValues({});
  });

  testWidgets('G777Sidebar renders logo and navigation items', (
    WidgetTester tester,
  ) async {
    // Create a simple router for testing
    final router = GoRouter(
      routes: [
        GoRoute(
          path: '/',
          builder: (context, state) => const Scaffold(body: G777Sidebar()),
        ),
      ],
    );

    await tester.pumpWidget(MaterialApp.router(routerConfig: router));

    // Verify Logo exists
    expect(find.text('G777'), findsOneWidget);

    // Verify Navigation Labels (some of them)
    expect(find.text('Dashboard'), findsOneWidget);
    expect(find.text('Members Grabber'), findsOneWidget);
    expect(find.text('Advanced Sender'), findsOneWidget);
    expect(find.text('Links Grabber'), findsOneWidget);
  });
}

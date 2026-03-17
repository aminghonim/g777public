import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/features/auth/presentation/pages/login_page.dart';

void main() {
  setUpAll(() {
    FlutterSecureStorage.setMockInitialValues({});
  });

  testWidgets('LoginPage renders correctly with Riverpod', (
    WidgetTester tester,
  ) async {
    // Build the login page within a ProviderScope
    await tester.pumpWidget(
      const ProviderScope(child: MaterialApp(home: LoginPage())),
    );

    // Give it a moment to finish initial animations
    await tester.pumpAndSettle();

    // Verify Brand Identity presence
    expect(find.text('G777'), findsOneWidget);
    expect(find.text('ULTIMATE'), findsOneWidget);

    // Verify UI Components
    expect(find.text('اسم المستخدم'), findsOneWidget);
    expect(find.text('كلمة المرور'), findsOneWidget);
    expect(find.text('دخول'), findsOneWidget);

    // Check for form fields
    expect(find.byType(TextFormField), findsNWidgets(2));
  });
}

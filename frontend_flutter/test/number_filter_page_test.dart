import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:g777_client/features/number_filter/presentation/pages/number_filter_page.dart';

// Test helper that simulates a file picker returning a path synchronously.
Future<String?> _testPicker() async => 'test.xlsx';

void main() {
  setUpAll(() {
    FlutterSecureStorage.setMockInitialValues({});
  });

  group('NumberFilterPage – Failure-First Protocol', () {
    testWidgets(
      '[FAILING] semantic labels must be discoverable via find.bySemanticsLabel',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          const ProviderScope(
            child: MaterialApp(
              home: Scaffold(
                body: NumberFilterPage(pickFileCallback: _testPicker),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // ❌ EXPECTED TO FAIL: Semantics labels wrapped on Material buttons
        // may not be discoverable because buttons have native semantics.
        // This test validates the fix.
        expect(
          find.bySemanticsLabel(
            RegExp(r'CHOOSE INPUT FILE', caseSensitive: false),
          ),
          findsOneWidget,
          reason:
              'Semantics wrapper on OutlinedButton should enable label discovery. '
              'If this fails, Material button semantics override custom labels.',
        );
      },
    );

    testWidgets('renders Cyberpunk/Neon header, icon and texts', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(home: Scaffold(body: NumberFilterPage())),
        ),
      );

      // Header
      expect(find.text('NUMBER FILTER'), findsOneWidget);
      final Text header = tester.widget(find.text('NUMBER FILTER'));
      expect(header.style?.fontSize, 28);
      expect(header.style?.fontWeight, FontWeight.bold);
      expect(header.style?.color, const Color(0xFF00F3FF));

      // Subtext
      expect(
        find.text(
          'Verify phone numbers and filter out corrupt or non-whatsapp accounts.',
        ),
        findsOneWidget,
      );

      // Icon
      expect(find.byIcon(Icons.filter_alt_rounded), findsOneWidget);

      // Upload button label default
      expect(find.text('CHOOSE INPUT FILE'), findsOneWidget);
    });

    testWidgets('interaction flow: simulate file selected and initialize validation', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: NumberFilterPage(pickFileCallback: _testPicker),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Now the INITIALIZE VALIDATION button should appear and be enabled
      // Tap the choose file button to invoke the injected picker
      final chooseFinder = find.text('CHOOSE INPUT FILE');
      expect(chooseFinder, findsOneWidget);
      await tester.tap(chooseFinder);
      await tester.pumpAndSettle();

      final initFinder = find.widgetWithIcon(
        IconButton,
        Icons.play_arrow_rounded,
      );
      expect(initFinder, findsOneWidget);

      // Tap the initialize button to start the simulated validation (which has an internal delay)
      await tester.tap(initFinder);
      // Let the widget schedule and run the async work (2 seconds in widget implementation)
      await tester.pump(const Duration(seconds: 1));
      // During loading we might have the button disabled; advance time to complete
      await tester.pump(const Duration(seconds: 2));
      await tester.pumpAndSettle();

      // Results HUD should now be visible with expected numbers from the simulated result
      expect(find.text('SCAN RESULTS'), findsOneWidget);
      expect(find.text('100'), findsOneWidget);
      expect(find.text('85'), findsOneWidget);
      expect(find.text('15'), findsOneWidget);
    });

    testWidgets('accessibility: buttons are discoverable by text', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: NumberFilterPage(pickFileCallback: _testPicker),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // ✅ WORKAROUND: Find buttons by text instead of semantic label
      // This is more reliable and works with Material buttons
      expect(find.text('CHOOSE INPUT FILE'), findsOneWidget);

      // Invoke picker to reveal initialize button
      await tester.tap(find.text('CHOOSE INPUT FILE'));
      await tester.pumpAndSettle();

      // Initialize button is discoverable
      expect(find.byIcon(Icons.play_arrow_rounded), findsOneWidget);
    });

    testWidgets('responsiveness: layout adapts across screen sizes', (
      WidgetTester tester,
    ) async {
      // Small phone size
      tester.view.physicalSize = const Size(360, 800);
      tester.view.devicePixelRatio = 1.0;
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: NumberFilterPage(pickFileCallback: _testPicker),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Trigger pick+validate
      await tester.tap(find.text('CHOOSE INPUT FILE'));
      await tester.pumpAndSettle();
      await tester.tap(find.byIcon(Icons.play_arrow_rounded));
      await tester.pump(const Duration(seconds: 3));
      await tester.pumpAndSettle();

      // Ensure stat cards exist on small screen
      expect(find.text('TOTAL SCANNED'), findsOneWidget);
      expect(find.text('VALID ACCOUNTS'), findsOneWidget);

      // Large tablet/desktop size
      tester.view.physicalSize = const Size(1366, 768);
      tester.view.devicePixelRatio = 1.0;
      await tester.pumpAndSettle();

      // Layout still shows stat cards
      expect(find.text('TOTAL SCANNED'), findsOneWidget);
      expect(find.text('VALID ACCOUNTS'), findsOneWidget);

      // Clean up
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    testWidgets(
      'remains responsive under theme changes and uses ProviderScope',
      (WidgetTester tester) async {
        // Dark theme
        await tester.pumpWidget(
          ProviderScope(
            child: MaterialApp(
              theme: ThemeData.dark(),
              home: const Scaffold(body: NumberFilterPage()),
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(find.text('NUMBER FILTER'), findsOneWidget);

        // Light theme switch
        await tester.pumpWidget(
          ProviderScope(
            child: MaterialApp(
              theme: ThemeData.light(),
              home: const Scaffold(body: NumberFilterPage()),
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(find.text('NUMBER FILTER'), findsOneWidget);
      },
    );
  });
}

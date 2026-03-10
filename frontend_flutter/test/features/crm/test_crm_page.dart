import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/features/crm/presentation/pages/crm_page.dart';
import 'package:g777_client/features/crm/providers/crm_provider.dart';
import 'package:g777_client/features/crm/data/crm_repository.dart';
import 'package:g777_client/shared/providers/locale_provider.dart';
import 'package:g777_client/shared/providers/theme_provider.dart';
import 'package:g777_client/l10n/app_localizations.dart';

import 'package:shared_preferences/shared_preferences.dart';
import 'package:g777_client/core/providers/shared_prefs_provider.dart';

void main() {
  testWidgets('CrmCustomersPage loads and displays basic UI', (WidgetTester tester) async {

    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
          customersProvider.overrideWith((ref) => CustomersNotifierMock()),
          crmStatsProvider.overrideWith((ref) => CrmStatsNotifierMock()),
        ],
        child: const MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: Locale('ar'),
          home: CrmCustomersPage(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('إدارة العملاء'), findsOneWidget);
    expect(find.text('إجمالي العملاء'), findsOneWidget);
    expect(find.text('عملاء محتملين'), findsOneWidget);
    expect(find.text('عملاء VIP'), findsOneWidget);
  });
}

class MockCrmRepository implements CrmRepository {
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class CustomersNotifierMock extends CustomersNotifier {
  CustomersNotifierMock() : super(MockCrmRepository()) {
    state = const AsyncValue.data([
      {
        'id': '1',
        'name': 'Test User',
        'phone': '123456789',
        'customer_type': 'vip',
        'city': 'Cairo',
      }
    ]);
  }

  @override
  Future<void> fetchCustomers({String? type, String? city, String? interests}) async {}
}

class CrmStatsNotifierMock extends CrmStatsNotifier {
  CrmStatsNotifierMock() : super(MockCrmRepository()) {
    state = const AsyncValue.data({
      'total_customers': 1,
      'by_type': {
        'vip': 1,
        'lead': 0,
        'customer': 0,
      }
    });
  }

  @override
  Future<void> fetchStats() async {}
}

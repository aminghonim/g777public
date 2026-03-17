import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/crm_repository.dart';

// Provides the Customer List State
final customersProvider = StateNotifierProvider<CustomersNotifier, AsyncValue<List<dynamic>>>((ref) {
  final repository = ref.watch(crmRepositoryProvider);
  return CustomersNotifier(repository);
});

class CustomersNotifier extends StateNotifier<AsyncValue<List<dynamic>>> {
  final CrmRepository _repository;

  CustomersNotifier(this._repository) : super(const AsyncValue.loading()) {
    fetchCustomers();
  }

  Future<void> fetchCustomers({String? type, String? city, String? interests}) async {
    state = const AsyncValue.loading();
    try {
      final customers = await _repository.getCustomers(
        type: type,
        city: city,
        interests: interests,
      );
      state = AsyncValue.data(customers);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> addTag(int customerId, String tag) async {
    try {
      await _repository.addTag(customerId, tag);
      // Refresh list to show new tag
      await fetchCustomers();
    } catch (e) {
      // Handle error natively or let UI catch it
      rethrow;
    }
  }

  Future<void> removeTag(int customerId, String tag) async {
    try {
      await _repository.removeTag(customerId, tag);
      // Refresh list
      await fetchCustomers();
    } catch (e) {
      rethrow;
    }
  }
}

// Provides the CRM Stats State
final crmStatsProvider = StateNotifierProvider<CrmStatsNotifier, AsyncValue<Map<String, dynamic>>>((ref) {
  final repository = ref.watch(crmRepositoryProvider);
  return CrmStatsNotifier(repository);
});

class CrmStatsNotifier extends StateNotifier<AsyncValue<Map<String, dynamic>>> {
  final CrmRepository _repository;

  CrmStatsNotifier(this._repository) : super(const AsyncValue.loading()) {
    fetchStats();
  }

  Future<void> fetchStats() async {
    state = const AsyncValue.loading();
    try {
      final stats = await _repository.getStats();
      state = AsyncValue.data(stats);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

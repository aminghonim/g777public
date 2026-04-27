import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/crm_repository.dart';

// Provides the Customer List State
final customersProvider =
    NotifierProvider<CustomersNotifier, AsyncValue<List<dynamic>>>(
  CustomersNotifier.new,
);

class CustomersNotifier extends Notifier<AsyncValue<List<dynamic>>> {
  @override
  AsyncValue<List<dynamic>> build() {
    final repository = ref.watch(crmRepositoryProvider);
    Future.microtask(() => fetchCustomers(repository: repository));
    return const AsyncValue.loading();
  }

  CrmRepository get _repository => ref.read(crmRepositoryProvider);

  Future<void> fetchCustomers({
    CrmRepository? repository,
    String? type,
    String? city,
    String? interests,
  }) async {
    state = const AsyncValue.loading();
    try {
      final repo = repository ?? _repository;
      final customers = await repo.getCustomers(
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
      await fetchCustomers();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> removeTag(int customerId, String tag) async {
    try {
      await _repository.removeTag(customerId, tag);
      await fetchCustomers();
    } catch (e) {
      rethrow;
    }
  }
}

// Provides the CRM Stats State
final crmStatsProvider =
    NotifierProvider<CrmStatsNotifier, AsyncValue<Map<String, dynamic>>>(
  CrmStatsNotifier.new,
);

class CrmStatsNotifier extends Notifier<AsyncValue<Map<String, dynamic>>> {
  @override
  AsyncValue<Map<String, dynamic>> build() {
    final repository = ref.watch(crmRepositoryProvider);
    Future.microtask(() => _fetchStats(repository));
    return const AsyncValue.loading();
  }

  Future<void> _fetchStats(CrmRepository repository) async {
    state = const AsyncValue.loading();
    try {
      final stats = await repository.getStats();
      state = AsyncValue.data(stats);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> fetchStats() async {
    await _fetchStats(ref.read(crmRepositoryProvider));
  }
}

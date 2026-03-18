import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/api_client.dart';

class QuotaService {
  final ApiClient _api;

  QuotaService(this._api);

  Future<Map<String, dynamic>> getQuota() async {
    final response = await _api.get('/users/quota');
    if (response.isSuccess) {
      return Map<String, dynamic>.from(response.data);
    }
    throw Exception('Failed to fetch quota');
  }
}

final quotaServiceProvider = Provider<QuotaService>((ref) {
  final api = ref.watch(apiClientProvider);
  return QuotaService(api);
});

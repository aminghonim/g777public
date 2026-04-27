import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/api_client.dart';

// Provides the repository instance
final crmRepositoryProvider = Provider<CrmRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return CrmRepository(apiClient);
});

class CrmRepository {
  final ApiClient _apiClient;

  CrmRepository(this._apiClient);

  Future<List<dynamic>> getCustomers({
    String? type,
    String? city,
    String? interests,
  }) async {
    final queryParams = <String, String>{};
    if (type != null && type.isNotEmpty) queryParams['customer_type'] = type;
    if (city != null && city.isNotEmpty) queryParams['city'] = city;
    if (interests != null && interests.isNotEmpty) {
      queryParams['interests'] = interests;
    }

    final response = await _apiClient.get('/api/crm/customers', queryParams: queryParams);
    return response.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> getStats() async {
    final response = await _apiClient.get('/api/crm/stats');
    return response.data as Map<String, dynamic>;
  }

  Future<bool> addTag(int customerId, String tag) async {
    final response = await _apiClient.post(
      '/api/crm/customers/$customerId/tags',
      body: {'tag': tag},
    );
    return response.isSuccess;
  }

  Future<bool> removeTag(int customerId, String tag) async {
    final response = await _apiClient.delete('/api/crm/customers/$customerId/tags/$tag');
    return response.isSuccess;
  }

  // Uses api_client to construct the export URL directly for LaunchUrl
  Future<String> getExportUrl() async {
    final baseUrl = await _apiClient.resolvedBaseUrl;
    return '$baseUrl/api/crm/export/csv';
  }
}

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/quota_service.dart';

final quotaProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final service = ref.watch(quotaServiceProvider);
  return service.getQuota();
});

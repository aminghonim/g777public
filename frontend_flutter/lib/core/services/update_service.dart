import 'package:g777_client/core/services/api_client.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class UpdateInfo {
  final bool hasUpdate;
  final String latestVersion;
  final String downloadUrl;
  final String sha256;
  final String? changelog;

  UpdateInfo({
    required this.hasUpdate,
    required this.latestVersion,
    required this.downloadUrl,
    required this.sha256,
    this.changelog,
  });

  factory UpdateInfo.fromJson(Map<String, dynamic> json) {
    return UpdateInfo(
      hasUpdate: json['has_update'] ?? false,
      latestVersion: json['latest_version'] ?? '',
      downloadUrl: json['download_url'] ?? '',
      sha256: json['sha256'] ?? '',
      changelog: json['changelog'],
    );
  }
}

class UpdateService {
  final ApiClient _api;

  UpdateService(this._api);

  Future<UpdateInfo> checkForUpdates() async {
    final res = await _api.get('/system/update/check');
    if (res.isSuccess) {
      return UpdateInfo.fromJson(res.data!);
    }
    throw Exception(res.data?['detail'] ?? 'Update check failed');
  }

  Future<void> applyUpdate(String downloadUrl, String sha256) async {
    final res = await _api.post(
      '/system/update/apply',
      body: {'download_url': downloadUrl, 'expected_hash': sha256},
    );
    if (!res.isSuccess) {
      throw Exception(res.data?['detail'] ?? 'Update application failed');
    }
  }
}

final updateServiceProvider = Provider(
  (ref) => UpdateService(ref.read(apiClientProvider)),
);

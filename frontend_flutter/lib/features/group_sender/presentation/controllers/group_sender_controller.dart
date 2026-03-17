import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:g777_client/core/services/api_client.dart';
import 'package:g777_client/shared/providers/logs_provider.dart';
import 'package:g777_client/core/providers/system_stream_provider.dart';
import 'dart:convert';

class GroupSenderState {
  final String? uploadedFileName;
  final String? uploadedFilePath;
  final String? directContacts; // JSON string of contacts
  final bool isLoading;
  final bool isCampaignRunning;
  final double progress;

  GroupSenderState({
    this.uploadedFileName,
    this.uploadedFilePath,
    this.directContacts,
    this.isLoading = false,
    this.isCampaignRunning = false,
    this.progress = 0.0,
  });

  GroupSenderState copyWith({
    String? uploadedFileName,
    String? uploadedFilePath,
    String? directContacts,
    bool? isLoading,
    bool? isCampaignRunning,
    double? progress,
  }) {
    return GroupSenderState(
      uploadedFileName: uploadedFileName ?? this.uploadedFileName,
      uploadedFilePath: uploadedFilePath ?? this.uploadedFilePath,
      directContacts: directContacts ?? this.directContacts,
      isLoading: isLoading ?? this.isLoading,
      isCampaignRunning: isCampaignRunning ?? this.isCampaignRunning,
      progress: progress ?? this.progress,
    );
  }
}

class GroupSenderNotifier extends StateNotifier<GroupSenderState> {
  final Ref ref;

  GroupSenderNotifier(this.ref) : super(GroupSenderState());

  ApiClient get _api => ref.read(apiClientProvider);

  void setDirectContact({required String phone, required String name}) {
    final contacts = [
      {'phone': phone, 'name': name},
    ];
    // Reset state for single send
    state = state.copyWith(
      directContacts: jsonEncode(contacts),
      uploadedFileName: null,
      uploadedFilePath: null,
      progress: 0.0,
    );
    ref
        .read(logsProvider.notifier)
        .addLog('Target Selected: $name ($phone)', type: LogType.success);
  }

  Future<void> pickAndUploadExcel() async {
    state = state.copyWith(isLoading: true, directContacts: null);
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['xlsx', 'xls'],
      );

      if (result != null && result.files.single.path != null) {
        final path = result.files.single.path!;
        final name = result.files.single.name;

        ref
            .read(logsProvider.notifier)
            .addLog('Uploading $name to backend...', type: LogType.info);

        final res = await _api.multipartPost(
          '/api/group_sender/upload',
          fields: {},
          filePath: path,
        );

        if (res.isSuccess) {
          state = state.copyWith(
            uploadedFileName: name,
            uploadedFilePath: path,
            isLoading: false,
          );
          ref
              .read(logsProvider.notifier)
              .addLog(
                'File uploaded successfully: $name',
                type: LogType.success,
              );
        } else {
          throw Exception(res.data?['error'] ?? 'Upload failed');
        }
      } else {
        state = state.copyWith(isLoading: false);
      }
    } catch (e) {
      state = state.copyWith(isLoading: false);
      ref
          .read(logsProvider.notifier)
          .addLog('Upload Error: $e', type: LogType.error);
    }
  }

  Future<void> launchCampaign({
    required List<String> messages,
    required String? groupLink,
    required int delayMin,
    required int delayMax,
  }) async {
    if (state.uploadedFileName == null && state.directContacts == null) {
      ref
          .read(logsProvider.notifier)
          .addLog('Error: No contacts source selected.', type: LogType.error);
      return;
    }

    state = state.copyWith(isCampaignRunning: true, progress: 0.0);
    ref
        .read(logsProvider.notifier)
        .addLog(
          'Launching campaign with ${messages.length} variants...',
          type: LogType.info,
        );

    try {
      final resMultipart = await _api.multipartPost(
        '/api/group_sender/launch',
        fields: {
          'messages': jsonEncode(messages),
          'sheet_name': 'Sheet1',
          'file_name': state.uploadedFileName ?? '',
          'direct_contacts': state.directContacts ?? '',
          'delay_min': delayMin.toString(),
          'delay_max': delayMax.toString(),
          'group_link': groupLink ?? '',
        },
        filePath: '', // No media for now
        fileField: 'media_file',
      );

      if (resMultipart.isSuccess) {
        ref
            .read(logsProvider.notifier)
            .addLog('Campaign successfully initiated.', type: LogType.success);
        // No need to call _listenToProgress() here,
        // the UI or a global listener already handles campaignStreamProvider.
      } else {
        throw Exception(resMultipart.data?['error'] ?? 'Launch failed');
      }
    } catch (e) {
      state = state.copyWith(isCampaignRunning: false);
      ref
          .read(logsProvider.notifier)
          .addLog('Launch Error: $e', type: LogType.error);
    }
  }

  /// NEW: Internal method to sync state with the unified SSE data
  void updateFromStream(Map<String, dynamic> campaignData) {
    if (campaignData.containsKey('total')) {
      final total = campaignData['total'] as int;
      final sent = campaignData['sent'] as int;
      final failed = campaignData['failed'] as int;
      final progress = total > 0 ? (sent + failed) / total : 0.0;

      state = state.copyWith(
        isCampaignRunning: campaignData['is_running'] ?? false,
        progress: progress,
      );
    }

    if (campaignData.containsKey('logs')) {
      final logs = campaignData['logs'] as List;
      if (logs.isNotEmpty) {
        // Log handled via logsStreamProvider globally
      }
    }
  }
}

/// A top-level listener that bridges the campaign stream to the controller
final campaignStreamListenerProvider = Provider<void>((ref) {
  ref.listen(campaignStreamProvider, (prev, next) {
    next.whenData((event) {
      if (event['type'] == 'CAMPAIGN') {
        final data = event['data'];
        if (data != null) {
          ref.read(groupSenderProvider.notifier).updateFromStream(data);
        }
      }
    });
  });
});

final groupSenderProvider =
    StateNotifierProvider<GroupSenderNotifier, GroupSenderState>((ref) {
      return GroupSenderNotifier(ref);
    });

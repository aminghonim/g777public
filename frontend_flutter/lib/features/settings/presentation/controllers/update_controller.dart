import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/update_service.dart';

class UpdateState {
  final bool isLoading;
  final UpdateInfo? updateInfo;
  final String? error;
  final bool isApplying;

  UpdateState({
    this.isLoading = false,
    this.updateInfo,
    this.error,
    this.isApplying = false,
  });

  UpdateState copyWith({
    bool? isLoading,
    UpdateInfo? updateInfo,
    String? error,
    bool? isApplying,
  }) {
    return UpdateState(
      isLoading: isLoading ?? this.isLoading,
      updateInfo: updateInfo ?? this.updateInfo,
      error: error,
      isApplying: isApplying ?? this.isApplying,
    );
  }
}

class UpdateNotifier extends Notifier<UpdateState> {
  @override
  UpdateState build() => UpdateState();

  UpdateService get _service => ref.read(updateServiceProvider);

  Future<void> checkForUpdates() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final info = await _service.checkForUpdates();
      state = state.copyWith(isLoading: false, updateInfo: info);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> applyUpdate() async {
    final info = state.updateInfo;
    if (info == null) return;

    state = state.copyWith(isApplying: true, error: null);
    try {
      await _service.applyUpdate(info.downloadUrl, info.sha256);
    } catch (e) {
      state = state.copyWith(isApplying: false, error: e.toString());
    }
  }
}

final updateControllerProvider = NotifierProvider<UpdateNotifier, UpdateState>(
  UpdateNotifier.new,
);

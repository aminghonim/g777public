import 'dart:async';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../data/evolution_service.dart';

part 'evolution_provider.g.dart';

/// SAAS-011: Logic State for the WhatsApp Evolution Lifecycle.
sealed class EvolutionState {
  const EvolutionState();
}

class EvolutionInitial extends EvolutionState {
  const EvolutionInitial();
}

class EvolutionLoading extends EvolutionState {
  const EvolutionLoading();
}

class EvolutionQRReceived extends EvolutionState {
  final String qrBase64;
  const EvolutionQRReceived(this.qrBase64);
}

class EvolutionConnected extends EvolutionState {
  const EvolutionConnected();
}

class EvolutionError extends EvolutionState {
  final String message;
  const EvolutionError(this.message);
}

@riverpod
class EvolutionController extends _$EvolutionController {
  Timer? _statusTimer;

  @override
  FutureOr<EvolutionState> build() async {
    // Automatically clean up timer when provider is destroyed
    ref.onDispose(() => _statusTimer?.cancel());

    // Initial status check on build
    return await _checkStatusSilently();
  }

  /// Silently checks status without triggering a full loading state.
  Future<EvolutionState> _checkStatusSilently() async {
    try {
      final service = await ref.read(evolutionServiceProvider.future);
      final statusData = await service.getStatus();
      final status = statusData['state'] as String;

      if (status == 'CONNECTED' || status == 'open') {
        _statusTimer?.cancel();
        return const EvolutionConnected();
      } else {
        return const EvolutionInitial();
      }
    } on EvolutionException catch (e) {
      // 403 or 404 indicates no instance is currently active for this tenant
      if (e.statusCode == 403 ||
          e.statusCode == 404 ||
          e.message.contains('No instance bound')) {
        return const EvolutionInitial();
      }
      return EvolutionError(e.message);
    } catch (_) {
      return const EvolutionInitial();
    }
  }

  /// SAAS-011: Main entry point for a user to start their WhatsApp connection flow.
  Future<void> initializeConnection() async {
    state = const AsyncLoading();
    try {
      final service = await ref.read(evolutionServiceProvider.future);

      // 1. Logic: Check if instance exists first to avoid double-allocation
      final statusCheck = await _checkStatusSilently();
      if (statusCheck is EvolutionConnected) {
        state = const AsyncData(EvolutionConnected());
        return;
      }

      // 2. Create Instance (Dynamic Tenant Provisioning)
      final createResponse = await service.createInstance();
      final qrBase64 = createResponse['qr_code_base64'] as String?;

      if (qrBase64 != null && qrBase64.isNotEmpty) {
        state = AsyncData(EvolutionQRReceived(qrBase64));
      } else {
        // 3. If QR didn't return in create, fetch it explicitly
        final qrResponse = await service.getQRCode();
        final fetchedQR = qrResponse['qr_code_base64'] as String;
        state = AsyncData(EvolutionQRReceived(fetchedQR));
      }

      // 4. Start polling server to detect when user scans the QR
      _startStatusPolling();
    } on EvolutionException catch (e) {
      state = AsyncData(EvolutionError(e.message));
    } catch (e) {
      state = const AsyncData(
        EvolutionError('Failed to initialize WhatsApp connection.'),
      );
    }
  }

  /// Polls the server every 5 seconds until connection is established.
  void _startStatusPolling() {
    _statusTimer?.cancel();
    _statusTimer = Timer.periodic(const Duration(seconds: 5), (timer) async {
      try {
        final service = await ref.read(evolutionServiceProvider.future);
        final statusData = await service.getStatus();
        final status = statusData['state'] as String;

        if (status == 'CONNECTED' || status == 'open') {
          timer.cancel();
          state = const AsyncData(EvolutionConnected());
        }
      } catch (_) {
        // Continue polling if request fails temporarily
      }
    });
  }

  /// SAAS-011: Securely tear down the instance and clean up resources.
  Future<void> disconnect() async {
    state = const AsyncLoading();
    try {
      final service = await ref.read(evolutionServiceProvider.future);
      await service.deleteInstance();
      _statusTimer?.cancel();
      state = const AsyncData(EvolutionInitial());
    } on EvolutionException catch (e) {
      state = AsyncData(EvolutionError(e.message));
    } catch (e) {
      state = const AsyncData(
        EvolutionError('Failed to properly disconnect instance.'),
      );
    }
  }

  /// Retries the connection from the current state (e.g., after an error).
  Future<void> retry() async {
    return initializeConnection();
  }
}

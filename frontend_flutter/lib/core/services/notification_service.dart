import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:developer' as dev;

/// G777 Notification Service
/// Handles system-level alert notifications for long-running tasks.
class NotificationService {
  // Singleton pattern
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _notificationsPlugin =
      FlutterLocalNotificationsPlugin();

  bool _initialized = false;

  /// Initialize the notification plugin with platform-specific settings.
  Future<void> init() async {
    if (_initialized) return;

    // Linux-specific initialization
    final LinuxInitializationSettings initializationSettingsLinux =
        LinuxInitializationSettings(
      defaultActionName: 'Open',
      defaultIcon: AssetsLinuxIcon('assets/icons/hex/logo.png'),
    );

    final InitializationSettings initializationSettings = InitializationSettings(
      linux: initializationSettingsLinux,
    );

    try {
      await _notificationsPlugin.initialize(
        initializationSettings,
        onDidReceiveNotificationResponse: (NotificationResponse response) {
          dev.log('Notification clicked: ${response.payload}', name: 'G777.Notifications');
        },
      );
      _initialized = true;
      dev.log('NotificationService initialized successfully', name: 'G777.Notifications');
    } catch (e) {
      dev.log('FAILED to initialize NotificationService: $e', name: 'G777.Notifications');
    }
  }

  /// Show a simple system notification.
  Future<void> showNotification({
    int id = 0,
    required String title,
    required String body,
    String? payload,
  }) async {
    if (!_initialized) await init();

    const NotificationDetails notificationDetails = NotificationDetails(
      linux: LinuxNotificationDetails(
        urgency: LinuxNotificationUrgency.normal,
      ),
    );

    try {
      await _notificationsPlugin.show(
        id,
        title,
        body,
        notificationDetails,
        payload: payload,
      );
      dev.log('System notification sent: $title', name: 'G777.Notifications');
    } catch (e) {
      dev.log('Error showing notification: $e', name: 'G777.Notifications');
    }
  }

  /// Specialized helpers for G777 Tasks
  Future<void> notifyTaskComplete(String taskName, String details) async {
    await showNotification(
      id: taskName.hashCode,
      title: '✅ Task Complete: $taskName',
      body: details,
    );
  }
}

// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'analytics_model.freezed.dart';
part 'analytics_model.g.dart';

@freezed
abstract class DailyActivity with _$DailyActivity {
  const factory DailyActivity({
    @JsonKey(name: 'usage_date') required String usageDate,
    @JsonKey(name: 'message_count') required int messageCount,
  }) = _DailyActivity;

  factory DailyActivity.fromJson(Map<String, dynamic> json) =>
      _$DailyActivityFromJson(json);
}

@freezed
abstract class AnalyticsModel with _$AnalyticsModel {
  const factory AnalyticsModel({
    @JsonKey(name: 'total_messages_sent') required int totalMessagesSent,
    @JsonKey(name: 'daily_usage') required int dailyUsage,
    @JsonKey(name: 'daily_limit') required int dailyLimit,
    @JsonKey(name: 'daily_remaining') required int dailyRemaining,
    @JsonKey(name: 'active_instances') required int activeInstances,
    @JsonKey(name: 'max_instances') required int maxInstances,
    @JsonKey(name: 'activity_7d') required List<DailyActivity> activity7d,
  }) = _AnalyticsModel;

  factory AnalyticsModel.fromJson(Map<String, dynamic> json) =>
      _$AnalyticsModelFromJson(json);
}

import 'package:freezed_annotation/freezed_annotation.dart';

part 'analytics_model.freezed.dart';
part 'analytics_model.g.dart';

@freezed
class DailyActivity with _$DailyActivity {
  // ignore: invalid_annotation_target
  const factory DailyActivity({
    // ignore: invalid_annotation_target
    @JsonKey(name: 'usage_date') required String usageDate,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'message_count') required int messageCount,
  }) = _DailyActivity;

  factory DailyActivity.fromJson(Map<String, dynamic> json) =>
      _$DailyActivityFromJson(json);
}

@freezed
class AnalyticsModel with _$AnalyticsModel {
  // ignore: invalid_annotation_target
  const factory AnalyticsModel({
    // ignore: invalid_annotation_target
    @JsonKey(name: 'total_messages_sent') required int totalMessagesSent,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'daily_usage') required int dailyUsage,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'daily_limit') required int dailyLimit,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'daily_remaining') required int dailyRemaining,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'active_instances') required int activeInstances,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'max_instances') required int maxInstances,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'activity_7d') required List<DailyActivity> activity7d,
  }) = _AnalyticsModel;

  factory AnalyticsModel.fromJson(Map<String, dynamic> json) =>
      _$AnalyticsModelFromJson(json);
}

// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'analytics_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_DailyActivity _$DailyActivityFromJson(Map<String, dynamic> json) =>
    _DailyActivity(
      usageDate: json['usage_date'] as String,
      messageCount: (json['message_count'] as num).toInt(),
    );

Map<String, dynamic> _$DailyActivityToJson(_DailyActivity instance) =>
    <String, dynamic>{
      'usage_date': instance.usageDate,
      'message_count': instance.messageCount,
    };

_AnalyticsModel _$AnalyticsModelFromJson(Map<String, dynamic> json) =>
    _AnalyticsModel(
      totalMessagesSent: (json['total_messages_sent'] as num).toInt(),
      dailyUsage: (json['daily_usage'] as num).toInt(),
      dailyLimit: (json['daily_limit'] as num).toInt(),
      dailyRemaining: (json['daily_remaining'] as num).toInt(),
      activeInstances: (json['active_instances'] as num).toInt(),
      maxInstances: (json['max_instances'] as num).toInt(),
      activity7d: (json['activity_7d'] as List<dynamic>)
          .map((e) => DailyActivity.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$AnalyticsModelToJson(_AnalyticsModel instance) =>
    <String, dynamic>{
      'total_messages_sent': instance.totalMessagesSent,
      'daily_usage': instance.dailyUsage,
      'daily_limit': instance.dailyLimit,
      'daily_remaining': instance.dailyRemaining,
      'active_instances': instance.activeInstances,
      'max_instances': instance.maxInstances,
      'activity_7d': instance.activity7d,
    };

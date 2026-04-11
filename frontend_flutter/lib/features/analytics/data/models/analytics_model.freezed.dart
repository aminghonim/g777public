// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'analytics_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

DailyActivity _$DailyActivityFromJson(Map<String, dynamic> json) {
  return _DailyActivity.fromJson(json);
}

/// @nodoc
mixin _$DailyActivity {
  @JsonKey(name: 'usage_date')
  String get usageDate => throw _privateConstructorUsedError;
  @JsonKey(name: 'message_count')
  int get messageCount => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $DailyActivityCopyWith<DailyActivity> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DailyActivityCopyWith<$Res> {
  factory $DailyActivityCopyWith(
          DailyActivity value, $Res Function(DailyActivity) then) =
      _$DailyActivityCopyWithImpl<$Res, DailyActivity>;
  @useResult
  $Res call(
      {@JsonKey(name: 'usage_date') String usageDate,
      @JsonKey(name: 'message_count') int messageCount});
}

/// @nodoc
class _$DailyActivityCopyWithImpl<$Res, $Val extends DailyActivity>
    implements $DailyActivityCopyWith<$Res> {
  _$DailyActivityCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? usageDate = null,
    Object? messageCount = null,
  }) {
    return _then(_value.copyWith(
      usageDate: null == usageDate
          ? _value.usageDate
          : usageDate // ignore: cast_nullable_to_non_nullable
              as String,
      messageCount: null == messageCount
          ? _value.messageCount
          : messageCount // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DailyActivityImplCopyWith<$Res>
    implements $DailyActivityCopyWith<$Res> {
  factory _$$DailyActivityImplCopyWith(
          _$DailyActivityImpl value, $Res Function(_$DailyActivityImpl) then) =
      __$$DailyActivityImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'usage_date') String usageDate,
      @JsonKey(name: 'message_count') int messageCount});
}

/// @nodoc
class __$$DailyActivityImplCopyWithImpl<$Res>
    extends _$DailyActivityCopyWithImpl<$Res, _$DailyActivityImpl>
    implements _$$DailyActivityImplCopyWith<$Res> {
  __$$DailyActivityImplCopyWithImpl(
      _$DailyActivityImpl _value, $Res Function(_$DailyActivityImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? usageDate = null,
    Object? messageCount = null,
  }) {
    return _then(_$DailyActivityImpl(
      usageDate: null == usageDate
          ? _value.usageDate
          : usageDate // ignore: cast_nullable_to_non_nullable
              as String,
      messageCount: null == messageCount
          ? _value.messageCount
          : messageCount // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DailyActivityImpl implements _DailyActivity {
  const _$DailyActivityImpl(
      {@JsonKey(name: 'usage_date') required this.usageDate,
      @JsonKey(name: 'message_count') required this.messageCount});

  factory _$DailyActivityImpl.fromJson(Map<String, dynamic> json) =>
      _$$DailyActivityImplFromJson(json);

  @override
  @JsonKey(name: 'usage_date')
  final String usageDate;
  @override
  @JsonKey(name: 'message_count')
  final int messageCount;

  @override
  String toString() {
    return 'DailyActivity(usageDate: $usageDate, messageCount: $messageCount)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DailyActivityImpl &&
            (identical(other.usageDate, usageDate) ||
                other.usageDate == usageDate) &&
            (identical(other.messageCount, messageCount) ||
                other.messageCount == messageCount));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(runtimeType, usageDate, messageCount);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$DailyActivityImplCopyWith<_$DailyActivityImpl> get copyWith =>
      __$$DailyActivityImplCopyWithImpl<_$DailyActivityImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DailyActivityImplToJson(
      this,
    );
  }
}

abstract class _DailyActivity implements DailyActivity {
  const factory _DailyActivity(
          {@JsonKey(name: 'usage_date') required final String usageDate,
          @JsonKey(name: 'message_count') required final int messageCount}) =
      _$DailyActivityImpl;

  factory _DailyActivity.fromJson(Map<String, dynamic> json) =
      _$DailyActivityImpl.fromJson;

  @override
  @JsonKey(name: 'usage_date')
  String get usageDate;
  @override
  @JsonKey(name: 'message_count')
  int get messageCount;
  @override
  @JsonKey(ignore: true)
  _$$DailyActivityImplCopyWith<_$DailyActivityImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

AnalyticsModel _$AnalyticsModelFromJson(Map<String, dynamic> json) {
  return _AnalyticsModel.fromJson(json);
}

/// @nodoc
mixin _$AnalyticsModel {
  @JsonKey(name: 'total_messages_sent')
  int get totalMessagesSent => throw _privateConstructorUsedError;
  @JsonKey(name: 'daily_usage')
  int get dailyUsage => throw _privateConstructorUsedError;
  @JsonKey(name: 'daily_limit')
  int get dailyLimit => throw _privateConstructorUsedError;
  @JsonKey(name: 'daily_remaining')
  int get dailyRemaining => throw _privateConstructorUsedError;
  @JsonKey(name: 'active_instances')
  int get activeInstances => throw _privateConstructorUsedError;
  @JsonKey(name: 'max_instances')
  int get maxInstances => throw _privateConstructorUsedError;
  @JsonKey(name: 'activity_7d')
  List<DailyActivity> get activity7d => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $AnalyticsModelCopyWith<AnalyticsModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AnalyticsModelCopyWith<$Res> {
  factory $AnalyticsModelCopyWith(
          AnalyticsModel value, $Res Function(AnalyticsModel) then) =
      _$AnalyticsModelCopyWithImpl<$Res, AnalyticsModel>;
  @useResult
  $Res call(
      {@JsonKey(name: 'total_messages_sent') int totalMessagesSent,
      @JsonKey(name: 'daily_usage') int dailyUsage,
      @JsonKey(name: 'daily_limit') int dailyLimit,
      @JsonKey(name: 'daily_remaining') int dailyRemaining,
      @JsonKey(name: 'active_instances') int activeInstances,
      @JsonKey(name: 'max_instances') int maxInstances,
      @JsonKey(name: 'activity_7d') List<DailyActivity> activity7d});
}

/// @nodoc
class _$AnalyticsModelCopyWithImpl<$Res, $Val extends AnalyticsModel>
    implements $AnalyticsModelCopyWith<$Res> {
  _$AnalyticsModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalMessagesSent = null,
    Object? dailyUsage = null,
    Object? dailyLimit = null,
    Object? dailyRemaining = null,
    Object? activeInstances = null,
    Object? maxInstances = null,
    Object? activity7d = null,
  }) {
    return _then(_value.copyWith(
      totalMessagesSent: null == totalMessagesSent
          ? _value.totalMessagesSent
          : totalMessagesSent // ignore: cast_nullable_to_non_nullable
              as int,
      dailyUsage: null == dailyUsage
          ? _value.dailyUsage
          : dailyUsage // ignore: cast_nullable_to_non_nullable
              as int,
      dailyLimit: null == dailyLimit
          ? _value.dailyLimit
          : dailyLimit // ignore: cast_nullable_to_non_nullable
              as int,
      dailyRemaining: null == dailyRemaining
          ? _value.dailyRemaining
          : dailyRemaining // ignore: cast_nullable_to_non_nullable
              as int,
      activeInstances: null == activeInstances
          ? _value.activeInstances
          : activeInstances // ignore: cast_nullable_to_non_nullable
              as int,
      maxInstances: null == maxInstances
          ? _value.maxInstances
          : maxInstances // ignore: cast_nullable_to_non_nullable
              as int,
      activity7d: null == activity7d
          ? _value.activity7d
          : activity7d // ignore: cast_nullable_to_non_nullable
              as List<DailyActivity>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AnalyticsModelImplCopyWith<$Res>
    implements $AnalyticsModelCopyWith<$Res> {
  factory _$$AnalyticsModelImplCopyWith(_$AnalyticsModelImpl value,
          $Res Function(_$AnalyticsModelImpl) then) =
      __$$AnalyticsModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'total_messages_sent') int totalMessagesSent,
      @JsonKey(name: 'daily_usage') int dailyUsage,
      @JsonKey(name: 'daily_limit') int dailyLimit,
      @JsonKey(name: 'daily_remaining') int dailyRemaining,
      @JsonKey(name: 'active_instances') int activeInstances,
      @JsonKey(name: 'max_instances') int maxInstances,
      @JsonKey(name: 'activity_7d') List<DailyActivity> activity7d});
}

/// @nodoc
class __$$AnalyticsModelImplCopyWithImpl<$Res>
    extends _$AnalyticsModelCopyWithImpl<$Res, _$AnalyticsModelImpl>
    implements _$$AnalyticsModelImplCopyWith<$Res> {
  __$$AnalyticsModelImplCopyWithImpl(
      _$AnalyticsModelImpl _value, $Res Function(_$AnalyticsModelImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalMessagesSent = null,
    Object? dailyUsage = null,
    Object? dailyLimit = null,
    Object? dailyRemaining = null,
    Object? activeInstances = null,
    Object? maxInstances = null,
    Object? activity7d = null,
  }) {
    return _then(_$AnalyticsModelImpl(
      totalMessagesSent: null == totalMessagesSent
          ? _value.totalMessagesSent
          : totalMessagesSent // ignore: cast_nullable_to_non_nullable
              as int,
      dailyUsage: null == dailyUsage
          ? _value.dailyUsage
          : dailyUsage // ignore: cast_nullable_to_non_nullable
              as int,
      dailyLimit: null == dailyLimit
          ? _value.dailyLimit
          : dailyLimit // ignore: cast_nullable_to_non_nullable
              as int,
      dailyRemaining: null == dailyRemaining
          ? _value.dailyRemaining
          : dailyRemaining // ignore: cast_nullable_to_non_nullable
              as int,
      activeInstances: null == activeInstances
          ? _value.activeInstances
          : activeInstances // ignore: cast_nullable_to_non_nullable
              as int,
      maxInstances: null == maxInstances
          ? _value.maxInstances
          : maxInstances // ignore: cast_nullable_to_non_nullable
              as int,
      activity7d: null == activity7d
          ? _value._activity7d
          : activity7d // ignore: cast_nullable_to_non_nullable
              as List<DailyActivity>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AnalyticsModelImpl implements _AnalyticsModel {
  const _$AnalyticsModelImpl(
      {@JsonKey(name: 'total_messages_sent') required this.totalMessagesSent,
      @JsonKey(name: 'daily_usage') required this.dailyUsage,
      @JsonKey(name: 'daily_limit') required this.dailyLimit,
      @JsonKey(name: 'daily_remaining') required this.dailyRemaining,
      @JsonKey(name: 'active_instances') required this.activeInstances,
      @JsonKey(name: 'max_instances') required this.maxInstances,
      @JsonKey(name: 'activity_7d')
      required final List<DailyActivity> activity7d})
      : _activity7d = activity7d;

  factory _$AnalyticsModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$AnalyticsModelImplFromJson(json);

  @override
  @JsonKey(name: 'total_messages_sent')
  final int totalMessagesSent;
  @override
  @JsonKey(name: 'daily_usage')
  final int dailyUsage;
  @override
  @JsonKey(name: 'daily_limit')
  final int dailyLimit;
  @override
  @JsonKey(name: 'daily_remaining')
  final int dailyRemaining;
  @override
  @JsonKey(name: 'active_instances')
  final int activeInstances;
  @override
  @JsonKey(name: 'max_instances')
  final int maxInstances;
  final List<DailyActivity> _activity7d;
  @override
  @JsonKey(name: 'activity_7d')
  List<DailyActivity> get activity7d {
    if (_activity7d is EqualUnmodifiableListView) return _activity7d;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_activity7d);
  }

  @override
  String toString() {
    return 'AnalyticsModel(totalMessagesSent: $totalMessagesSent, dailyUsage: $dailyUsage, dailyLimit: $dailyLimit, dailyRemaining: $dailyRemaining, activeInstances: $activeInstances, maxInstances: $maxInstances, activity7d: $activity7d)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AnalyticsModelImpl &&
            (identical(other.totalMessagesSent, totalMessagesSent) ||
                other.totalMessagesSent == totalMessagesSent) &&
            (identical(other.dailyUsage, dailyUsage) ||
                other.dailyUsage == dailyUsage) &&
            (identical(other.dailyLimit, dailyLimit) ||
                other.dailyLimit == dailyLimit) &&
            (identical(other.dailyRemaining, dailyRemaining) ||
                other.dailyRemaining == dailyRemaining) &&
            (identical(other.activeInstances, activeInstances) ||
                other.activeInstances == activeInstances) &&
            (identical(other.maxInstances, maxInstances) ||
                other.maxInstances == maxInstances) &&
            const DeepCollectionEquality()
                .equals(other._activity7d, _activity7d));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      totalMessagesSent,
      dailyUsage,
      dailyLimit,
      dailyRemaining,
      activeInstances,
      maxInstances,
      const DeepCollectionEquality().hash(_activity7d));

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$AnalyticsModelImplCopyWith<_$AnalyticsModelImpl> get copyWith =>
      __$$AnalyticsModelImplCopyWithImpl<_$AnalyticsModelImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AnalyticsModelImplToJson(
      this,
    );
  }
}

abstract class _AnalyticsModel implements AnalyticsModel {
  const factory _AnalyticsModel(
      {@JsonKey(name: 'total_messages_sent')
      required final int totalMessagesSent,
      @JsonKey(name: 'daily_usage') required final int dailyUsage,
      @JsonKey(name: 'daily_limit') required final int dailyLimit,
      @JsonKey(name: 'daily_remaining') required final int dailyRemaining,
      @JsonKey(name: 'active_instances') required final int activeInstances,
      @JsonKey(name: 'max_instances') required final int maxInstances,
      @JsonKey(name: 'activity_7d')
      required final List<DailyActivity> activity7d}) = _$AnalyticsModelImpl;

  factory _AnalyticsModel.fromJson(Map<String, dynamic> json) =
      _$AnalyticsModelImpl.fromJson;

  @override
  @JsonKey(name: 'total_messages_sent')
  int get totalMessagesSent;
  @override
  @JsonKey(name: 'daily_usage')
  int get dailyUsage;
  @override
  @JsonKey(name: 'daily_limit')
  int get dailyLimit;
  @override
  @JsonKey(name: 'daily_remaining')
  int get dailyRemaining;
  @override
  @JsonKey(name: 'active_instances')
  int get activeInstances;
  @override
  @JsonKey(name: 'max_instances')
  int get maxInstances;
  @override
  @JsonKey(name: 'activity_7d')
  List<DailyActivity> get activity7d;
  @override
  @JsonKey(ignore: true)
  _$$AnalyticsModelImplCopyWith<_$AnalyticsModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

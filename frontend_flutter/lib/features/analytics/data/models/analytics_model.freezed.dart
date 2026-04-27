// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'analytics_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$DailyActivity {

@JsonKey(name: 'usage_date') String get usageDate;@JsonKey(name: 'message_count') int get messageCount;
/// Create a copy of DailyActivity
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DailyActivityCopyWith<DailyActivity> get copyWith => _$DailyActivityCopyWithImpl<DailyActivity>(this as DailyActivity, _$identity);

  /// Serializes this DailyActivity to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DailyActivity&&(identical(other.usageDate, usageDate) || other.usageDate == usageDate)&&(identical(other.messageCount, messageCount) || other.messageCount == messageCount));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,usageDate,messageCount);

@override
String toString() {
  return 'DailyActivity(usageDate: $usageDate, messageCount: $messageCount)';
}


}

/// @nodoc
abstract mixin class $DailyActivityCopyWith<$Res>  {
  factory $DailyActivityCopyWith(DailyActivity value, $Res Function(DailyActivity) _then) = _$DailyActivityCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'usage_date') String usageDate,@JsonKey(name: 'message_count') int messageCount
});




}
/// @nodoc
class _$DailyActivityCopyWithImpl<$Res>
    implements $DailyActivityCopyWith<$Res> {
  _$DailyActivityCopyWithImpl(this._self, this._then);

  final DailyActivity _self;
  final $Res Function(DailyActivity) _then;

/// Create a copy of DailyActivity
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? usageDate = null,Object? messageCount = null,}) {
  return _then(_self.copyWith(
usageDate: null == usageDate ? _self.usageDate : usageDate // ignore: cast_nullable_to_non_nullable
as String,messageCount: null == messageCount ? _self.messageCount : messageCount // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [DailyActivity].
extension DailyActivityPatterns on DailyActivity {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DailyActivity value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DailyActivity() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DailyActivity value)  $default,){
final _that = this;
switch (_that) {
case _DailyActivity():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DailyActivity value)?  $default,){
final _that = this;
switch (_that) {
case _DailyActivity() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'usage_date')  String usageDate, @JsonKey(name: 'message_count')  int messageCount)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DailyActivity() when $default != null:
return $default(_that.usageDate,_that.messageCount);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'usage_date')  String usageDate, @JsonKey(name: 'message_count')  int messageCount)  $default,) {final _that = this;
switch (_that) {
case _DailyActivity():
return $default(_that.usageDate,_that.messageCount);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'usage_date')  String usageDate, @JsonKey(name: 'message_count')  int messageCount)?  $default,) {final _that = this;
switch (_that) {
case _DailyActivity() when $default != null:
return $default(_that.usageDate,_that.messageCount);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _DailyActivity implements DailyActivity {
  const _DailyActivity({@JsonKey(name: 'usage_date') required this.usageDate, @JsonKey(name: 'message_count') required this.messageCount});
  factory _DailyActivity.fromJson(Map<String, dynamic> json) => _$DailyActivityFromJson(json);

@override@JsonKey(name: 'usage_date') final  String usageDate;
@override@JsonKey(name: 'message_count') final  int messageCount;

/// Create a copy of DailyActivity
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DailyActivityCopyWith<_DailyActivity> get copyWith => __$DailyActivityCopyWithImpl<_DailyActivity>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DailyActivityToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DailyActivity&&(identical(other.usageDate, usageDate) || other.usageDate == usageDate)&&(identical(other.messageCount, messageCount) || other.messageCount == messageCount));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,usageDate,messageCount);

@override
String toString() {
  return 'DailyActivity(usageDate: $usageDate, messageCount: $messageCount)';
}


}

/// @nodoc
abstract mixin class _$DailyActivityCopyWith<$Res> implements $DailyActivityCopyWith<$Res> {
  factory _$DailyActivityCopyWith(_DailyActivity value, $Res Function(_DailyActivity) _then) = __$DailyActivityCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'usage_date') String usageDate,@JsonKey(name: 'message_count') int messageCount
});




}
/// @nodoc
class __$DailyActivityCopyWithImpl<$Res>
    implements _$DailyActivityCopyWith<$Res> {
  __$DailyActivityCopyWithImpl(this._self, this._then);

  final _DailyActivity _self;
  final $Res Function(_DailyActivity) _then;

/// Create a copy of DailyActivity
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? usageDate = null,Object? messageCount = null,}) {
  return _then(_DailyActivity(
usageDate: null == usageDate ? _self.usageDate : usageDate // ignore: cast_nullable_to_non_nullable
as String,messageCount: null == messageCount ? _self.messageCount : messageCount // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$AnalyticsModel {

@JsonKey(name: 'total_messages_sent') int get totalMessagesSent;@JsonKey(name: 'daily_usage') int get dailyUsage;@JsonKey(name: 'daily_limit') int get dailyLimit;@JsonKey(name: 'daily_remaining') int get dailyRemaining;@JsonKey(name: 'active_instances') int get activeInstances;@JsonKey(name: 'max_instances') int get maxInstances;@JsonKey(name: 'activity_7d') List<DailyActivity> get activity7d;
/// Create a copy of AnalyticsModel
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AnalyticsModelCopyWith<AnalyticsModel> get copyWith => _$AnalyticsModelCopyWithImpl<AnalyticsModel>(this as AnalyticsModel, _$identity);

  /// Serializes this AnalyticsModel to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AnalyticsModel&&(identical(other.totalMessagesSent, totalMessagesSent) || other.totalMessagesSent == totalMessagesSent)&&(identical(other.dailyUsage, dailyUsage) || other.dailyUsage == dailyUsage)&&(identical(other.dailyLimit, dailyLimit) || other.dailyLimit == dailyLimit)&&(identical(other.dailyRemaining, dailyRemaining) || other.dailyRemaining == dailyRemaining)&&(identical(other.activeInstances, activeInstances) || other.activeInstances == activeInstances)&&(identical(other.maxInstances, maxInstances) || other.maxInstances == maxInstances)&&const DeepCollectionEquality().equals(other.activity7d, activity7d));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,totalMessagesSent,dailyUsage,dailyLimit,dailyRemaining,activeInstances,maxInstances,const DeepCollectionEquality().hash(activity7d));

@override
String toString() {
  return 'AnalyticsModel(totalMessagesSent: $totalMessagesSent, dailyUsage: $dailyUsage, dailyLimit: $dailyLimit, dailyRemaining: $dailyRemaining, activeInstances: $activeInstances, maxInstances: $maxInstances, activity7d: $activity7d)';
}


}

/// @nodoc
abstract mixin class $AnalyticsModelCopyWith<$Res>  {
  factory $AnalyticsModelCopyWith(AnalyticsModel value, $Res Function(AnalyticsModel) _then) = _$AnalyticsModelCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'total_messages_sent') int totalMessagesSent,@JsonKey(name: 'daily_usage') int dailyUsage,@JsonKey(name: 'daily_limit') int dailyLimit,@JsonKey(name: 'daily_remaining') int dailyRemaining,@JsonKey(name: 'active_instances') int activeInstances,@JsonKey(name: 'max_instances') int maxInstances,@JsonKey(name: 'activity_7d') List<DailyActivity> activity7d
});




}
/// @nodoc
class _$AnalyticsModelCopyWithImpl<$Res>
    implements $AnalyticsModelCopyWith<$Res> {
  _$AnalyticsModelCopyWithImpl(this._self, this._then);

  final AnalyticsModel _self;
  final $Res Function(AnalyticsModel) _then;

/// Create a copy of AnalyticsModel
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? totalMessagesSent = null,Object? dailyUsage = null,Object? dailyLimit = null,Object? dailyRemaining = null,Object? activeInstances = null,Object? maxInstances = null,Object? activity7d = null,}) {
  return _then(_self.copyWith(
totalMessagesSent: null == totalMessagesSent ? _self.totalMessagesSent : totalMessagesSent // ignore: cast_nullable_to_non_nullable
as int,dailyUsage: null == dailyUsage ? _self.dailyUsage : dailyUsage // ignore: cast_nullable_to_non_nullable
as int,dailyLimit: null == dailyLimit ? _self.dailyLimit : dailyLimit // ignore: cast_nullable_to_non_nullable
as int,dailyRemaining: null == dailyRemaining ? _self.dailyRemaining : dailyRemaining // ignore: cast_nullable_to_non_nullable
as int,activeInstances: null == activeInstances ? _self.activeInstances : activeInstances // ignore: cast_nullable_to_non_nullable
as int,maxInstances: null == maxInstances ? _self.maxInstances : maxInstances // ignore: cast_nullable_to_non_nullable
as int,activity7d: null == activity7d ? _self.activity7d : activity7d // ignore: cast_nullable_to_non_nullable
as List<DailyActivity>,
  ));
}

}


/// Adds pattern-matching-related methods to [AnalyticsModel].
extension AnalyticsModelPatterns on AnalyticsModel {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AnalyticsModel value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AnalyticsModel() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AnalyticsModel value)  $default,){
final _that = this;
switch (_that) {
case _AnalyticsModel():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AnalyticsModel value)?  $default,){
final _that = this;
switch (_that) {
case _AnalyticsModel() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'total_messages_sent')  int totalMessagesSent, @JsonKey(name: 'daily_usage')  int dailyUsage, @JsonKey(name: 'daily_limit')  int dailyLimit, @JsonKey(name: 'daily_remaining')  int dailyRemaining, @JsonKey(name: 'active_instances')  int activeInstances, @JsonKey(name: 'max_instances')  int maxInstances, @JsonKey(name: 'activity_7d')  List<DailyActivity> activity7d)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AnalyticsModel() when $default != null:
return $default(_that.totalMessagesSent,_that.dailyUsage,_that.dailyLimit,_that.dailyRemaining,_that.activeInstances,_that.maxInstances,_that.activity7d);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'total_messages_sent')  int totalMessagesSent, @JsonKey(name: 'daily_usage')  int dailyUsage, @JsonKey(name: 'daily_limit')  int dailyLimit, @JsonKey(name: 'daily_remaining')  int dailyRemaining, @JsonKey(name: 'active_instances')  int activeInstances, @JsonKey(name: 'max_instances')  int maxInstances, @JsonKey(name: 'activity_7d')  List<DailyActivity> activity7d)  $default,) {final _that = this;
switch (_that) {
case _AnalyticsModel():
return $default(_that.totalMessagesSent,_that.dailyUsage,_that.dailyLimit,_that.dailyRemaining,_that.activeInstances,_that.maxInstances,_that.activity7d);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'total_messages_sent')  int totalMessagesSent, @JsonKey(name: 'daily_usage')  int dailyUsage, @JsonKey(name: 'daily_limit')  int dailyLimit, @JsonKey(name: 'daily_remaining')  int dailyRemaining, @JsonKey(name: 'active_instances')  int activeInstances, @JsonKey(name: 'max_instances')  int maxInstances, @JsonKey(name: 'activity_7d')  List<DailyActivity> activity7d)?  $default,) {final _that = this;
switch (_that) {
case _AnalyticsModel() when $default != null:
return $default(_that.totalMessagesSent,_that.dailyUsage,_that.dailyLimit,_that.dailyRemaining,_that.activeInstances,_that.maxInstances,_that.activity7d);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AnalyticsModel implements AnalyticsModel {
  const _AnalyticsModel({@JsonKey(name: 'total_messages_sent') required this.totalMessagesSent, @JsonKey(name: 'daily_usage') required this.dailyUsage, @JsonKey(name: 'daily_limit') required this.dailyLimit, @JsonKey(name: 'daily_remaining') required this.dailyRemaining, @JsonKey(name: 'active_instances') required this.activeInstances, @JsonKey(name: 'max_instances') required this.maxInstances, @JsonKey(name: 'activity_7d') required final  List<DailyActivity> activity7d}): _activity7d = activity7d;
  factory _AnalyticsModel.fromJson(Map<String, dynamic> json) => _$AnalyticsModelFromJson(json);

@override@JsonKey(name: 'total_messages_sent') final  int totalMessagesSent;
@override@JsonKey(name: 'daily_usage') final  int dailyUsage;
@override@JsonKey(name: 'daily_limit') final  int dailyLimit;
@override@JsonKey(name: 'daily_remaining') final  int dailyRemaining;
@override@JsonKey(name: 'active_instances') final  int activeInstances;
@override@JsonKey(name: 'max_instances') final  int maxInstances;
 final  List<DailyActivity> _activity7d;
@override@JsonKey(name: 'activity_7d') List<DailyActivity> get activity7d {
  if (_activity7d is EqualUnmodifiableListView) return _activity7d;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_activity7d);
}


/// Create a copy of AnalyticsModel
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AnalyticsModelCopyWith<_AnalyticsModel> get copyWith => __$AnalyticsModelCopyWithImpl<_AnalyticsModel>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AnalyticsModelToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _AnalyticsModel&&(identical(other.totalMessagesSent, totalMessagesSent) || other.totalMessagesSent == totalMessagesSent)&&(identical(other.dailyUsage, dailyUsage) || other.dailyUsage == dailyUsage)&&(identical(other.dailyLimit, dailyLimit) || other.dailyLimit == dailyLimit)&&(identical(other.dailyRemaining, dailyRemaining) || other.dailyRemaining == dailyRemaining)&&(identical(other.activeInstances, activeInstances) || other.activeInstances == activeInstances)&&(identical(other.maxInstances, maxInstances) || other.maxInstances == maxInstances)&&const DeepCollectionEquality().equals(other._activity7d, _activity7d));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,totalMessagesSent,dailyUsage,dailyLimit,dailyRemaining,activeInstances,maxInstances,const DeepCollectionEquality().hash(_activity7d));

@override
String toString() {
  return 'AnalyticsModel(totalMessagesSent: $totalMessagesSent, dailyUsage: $dailyUsage, dailyLimit: $dailyLimit, dailyRemaining: $dailyRemaining, activeInstances: $activeInstances, maxInstances: $maxInstances, activity7d: $activity7d)';
}


}

/// @nodoc
abstract mixin class _$AnalyticsModelCopyWith<$Res> implements $AnalyticsModelCopyWith<$Res> {
  factory _$AnalyticsModelCopyWith(_AnalyticsModel value, $Res Function(_AnalyticsModel) _then) = __$AnalyticsModelCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'total_messages_sent') int totalMessagesSent,@JsonKey(name: 'daily_usage') int dailyUsage,@JsonKey(name: 'daily_limit') int dailyLimit,@JsonKey(name: 'daily_remaining') int dailyRemaining,@JsonKey(name: 'active_instances') int activeInstances,@JsonKey(name: 'max_instances') int maxInstances,@JsonKey(name: 'activity_7d') List<DailyActivity> activity7d
});




}
/// @nodoc
class __$AnalyticsModelCopyWithImpl<$Res>
    implements _$AnalyticsModelCopyWith<$Res> {
  __$AnalyticsModelCopyWithImpl(this._self, this._then);

  final _AnalyticsModel _self;
  final $Res Function(_AnalyticsModel) _then;

/// Create a copy of AnalyticsModel
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? totalMessagesSent = null,Object? dailyUsage = null,Object? dailyLimit = null,Object? dailyRemaining = null,Object? activeInstances = null,Object? maxInstances = null,Object? activity7d = null,}) {
  return _then(_AnalyticsModel(
totalMessagesSent: null == totalMessagesSent ? _self.totalMessagesSent : totalMessagesSent // ignore: cast_nullable_to_non_nullable
as int,dailyUsage: null == dailyUsage ? _self.dailyUsage : dailyUsage // ignore: cast_nullable_to_non_nullable
as int,dailyLimit: null == dailyLimit ? _self.dailyLimit : dailyLimit // ignore: cast_nullable_to_non_nullable
as int,dailyRemaining: null == dailyRemaining ? _self.dailyRemaining : dailyRemaining // ignore: cast_nullable_to_non_nullable
as int,activeInstances: null == activeInstances ? _self.activeInstances : activeInstances // ignore: cast_nullable_to_non_nullable
as int,maxInstances: null == maxInstances ? _self.maxInstances : maxInstances // ignore: cast_nullable_to_non_nullable
as int,activity7d: null == activity7d ? _self._activity7d : activity7d // ignore: cast_nullable_to_non_nullable
as List<DailyActivity>,
  ));
}


}

// dart format on

// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'analytics_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(Analytics)
final analyticsProvider = AnalyticsProvider._();

final class AnalyticsProvider
    extends $AsyncNotifierProvider<Analytics, AnalyticsModel> {
  AnalyticsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'analyticsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$analyticsHash();

  @$internal
  @override
  Analytics create() => Analytics();
}

String _$analyticsHash() => r'cd93d54ced161e7c912aa7a1f07da9752faf7d19';

abstract class _$Analytics extends $AsyncNotifier<AnalyticsModel> {
  FutureOr<AnalyticsModel> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<AnalyticsModel>, AnalyticsModel>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<AnalyticsModel>, AnalyticsModel>,
              AsyncValue<AnalyticsModel>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

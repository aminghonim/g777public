// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'analytics_repository.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(analyticsRepository)
final analyticsRepositoryProvider = AnalyticsRepositoryProvider._();

final class AnalyticsRepositoryProvider
    extends
        $FunctionalProvider<
          AsyncValue<AnalyticsRepository>,
          AnalyticsRepository,
          FutureOr<AnalyticsRepository>
        >
    with
        $FutureModifier<AnalyticsRepository>,
        $FutureProvider<AnalyticsRepository> {
  AnalyticsRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'analyticsRepositoryProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$analyticsRepositoryHash();

  @$internal
  @override
  $FutureProviderElement<AnalyticsRepository> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<AnalyticsRepository> create(Ref ref) {
    return analyticsRepository(ref);
  }
}

String _$analyticsRepositoryHash() =>
    r'44030dd894a454b023e227a97f52908c4a5ff628';

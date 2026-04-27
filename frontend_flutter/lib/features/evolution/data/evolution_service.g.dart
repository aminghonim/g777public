// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'evolution_service.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(evolutionService)
final evolutionServiceProvider = EvolutionServiceProvider._();

final class EvolutionServiceProvider
    extends
        $FunctionalProvider<
          AsyncValue<EvolutionService>,
          EvolutionService,
          FutureOr<EvolutionService>
        >
    with $FutureModifier<EvolutionService>, $FutureProvider<EvolutionService> {
  EvolutionServiceProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'evolutionServiceProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$evolutionServiceHash();

  @$internal
  @override
  $FutureProviderElement<EvolutionService> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<EvolutionService> create(Ref ref) {
    return evolutionService(ref);
  }
}

String _$evolutionServiceHash() => r'11b751061f306a6648b7729a07293fcdda54e1c0';

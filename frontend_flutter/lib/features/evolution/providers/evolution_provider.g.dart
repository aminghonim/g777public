// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'evolution_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(EvolutionController)
final evolutionControllerProvider = EvolutionControllerProvider._();

final class EvolutionControllerProvider
    extends $AsyncNotifierProvider<EvolutionController, EvolutionState> {
  EvolutionControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'evolutionControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$evolutionControllerHash();

  @$internal
  @override
  EvolutionController create() => EvolutionController();
}

String _$evolutionControllerHash() =>
    r'c20e37bbd7f7d8aa3df8062132124d774cc19638';

abstract class _$EvolutionController extends $AsyncNotifier<EvolutionState> {
  FutureOr<EvolutionState> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<EvolutionState>, EvolutionState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<EvolutionState>, EvolutionState>,
              AsyncValue<EvolutionState>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

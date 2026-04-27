// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'license_status_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(LicenseStatusNotifier)
final licenseStatusProvider = LicenseStatusNotifierProvider._();

final class LicenseStatusNotifierProvider
    extends $AsyncNotifierProvider<LicenseStatusNotifier, LicenseStatus> {
  LicenseStatusNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'licenseStatusProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$licenseStatusNotifierHash();

  @$internal
  @override
  LicenseStatusNotifier create() => LicenseStatusNotifier();
}

String _$licenseStatusNotifierHash() =>
    r'a181c8a0d64589bbcfbda8d6030360ac0ce5fe6a';

abstract class _$LicenseStatusNotifier extends $AsyncNotifier<LicenseStatus> {
  FutureOr<LicenseStatus> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<LicenseStatus>, LicenseStatus>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<LicenseStatus>, LicenseStatus>,
              AsyncValue<LicenseStatus>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

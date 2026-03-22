import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:g777_client/core/services/api_service.dart';
import 'package:g777_client/shared/providers/locale_provider.dart';
import 'package:g777_client/features/settings/presentation/controllers/settings_controller.dart';
import 'package:g777_client/features/settings/presentation/controllers/update_controller.dart';
import 'package:g777_client/features/settings/presentation/widgets/quota_dashboard_widget.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'package:g777_client/core/theme/theme.dart'; // Unified theme system

class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final themeController = ThemeController(ref);
    final currentStyle = ref.watch(themeStyleProvider);
    final l10n = AppLocalizations.of(context)!;
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      appBar: AppBar(
        title: Text(
          l10n.settings.toUpperCase(),
          style: const TextStyle(
            fontWeight: FontWeight.w900,
            fontFamily: 'Oxanium',
            letterSpacing: 2,
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SelectionArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            // SAAS-014: Quota Dashboard
            const QuotaDashboardWidget(),
            const SizedBox(height: 32),

            // 1. VISUALS & UX
            _buildSectionHeader(l10n.visualEngine.toUpperCase(), colorScheme),
            _buildSettingsCard(
              colorScheme,
              children: [
                _buildDropdownTile<ThemeStyle>(
                  label: l10n.systemThemeMode,
                  value: currentStyle,
                  items: ThemeStyle.values,
                  onChanged: (val) {
                    if (val != null) themeController.setThemeStyle(val);
                  },
                ),
                ListTile(
                  leading: Icon(
                    Icons.palette_rounded,
                    color: colorScheme.primary,
                  ),
                  title: const Text(
                    'Full Theme Customization / تخصيص الثيمات',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                  ),
                  trailing: const Icon(Icons.chevron_right_rounded),
                  onTap: () => context.push('/theme-settings'),
                ),
                ListTile(
                  title: Text(
                    l10n.languageIntegration,
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  subtitle: Text(
                    settings.language == 'en'
                        ? 'English (UK/US)'
                        : 'العربية (Arabic)',
                    style: const TextStyle(fontSize: 11),
                  ),
                  trailing: TextButton(
                    onPressed: () {
                      ref.read(localeProvider.notifier).toggleLocale();
                      ref
                          .read(settingsProvider.notifier)
                          .updateSettings(
                            settings.copyWith(
                              language: ref.read(localeProvider).languageCode,
                            ),
                          );
                    },
                    child: Text(
                      settings.language == 'en'
                          ? l10n.switchLanguage('AR')
                          : l10n.switchLanguage('EN'),
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 32),

            // 2. CONNECTIVITY NODE
            _buildSectionHeader(
              l10n.connectivityNode.toUpperCase(),
              colorScheme,
            ),
            _buildSettingsCard(
              colorScheme,
              children: [
                _buildTextFieldTile(
                  colorScheme: colorScheme,
                  label: l10n.evolutionApiHost,
                  initialValue: settings.evolutionApiUrl,
                  onChanged: (val) => ref
                      .read(settingsProvider.notifier)
                      .updateSettings(settings.copyWith(evolutionApiUrl: val)),
                ),
                _buildTextFieldTile(
                  colorScheme: colorScheme,
                  label: l10n.globalMasterKey,
                  initialValue: settings.globalApiKey,
                  isPassword: true,
                  onChanged: (val) => ref
                      .read(settingsProvider.notifier)
                      .updateSettings(settings.copyWith(globalApiKey: val)),
                ),
                ListTile(
                  leading: Icon(Icons.bolt_rounded, color: colorScheme.primary),
                  title: Text(
                    l10n.nodeHealthStatus,
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  trailing: TextButton(
                    onPressed: () async {
                      try {
                        final result = await ApiService().checkHealth();
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: SelectableText(
                                'NODE ONLINE: ${result['status'] ?? 'OK'}',
                                style: TextStyle(
                                  color: colorScheme.primary,
                                  fontWeight: FontWeight.bold,
                                  fontFamily: 'Oxanium',
                                  letterSpacing: 1.2,
                                ),
                              ),
                              backgroundColor:
                                  colorScheme.surfaceContainerHighest,
                              behavior: SnackBarBehavior.floating,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                                side: BorderSide(color: colorScheme.primary),
                              ),
                              duration: const Duration(seconds: 3),
                            ),
                          );
                        }
                      } catch (e) {
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: SelectableText(
                                'NODE OFFLINE: ${e.toString().split(':').first}',
                                style: TextStyle(
                                  color: colorScheme.dangerAccent,
                                  fontWeight: FontWeight.bold,
                                  fontFamily: 'Oxanium',
                                  letterSpacing: 1.2,
                                ),
                              ),
                              backgroundColor: colorScheme.dangerBackground,
                              behavior: SnackBarBehavior.floating,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                                side: BorderSide(
                                  color: colorScheme.dangerAccent,
                                ),
                              ),
                              duration: const Duration(seconds: 4),
                            ),
                          );
                        }
                      }
                    },
                    child: Text(l10n.pingServer.toUpperCase()),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 32),

            // 3. SAFETY PROTOCOLS
            _buildSectionHeader(
              l10n.safetyProtocols.toUpperCase(),
              colorScheme,
            ),
            _buildSettingsCard(
              colorScheme,
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.messageBatchDelay(
                          settings.minDelay,
                          settings.maxDelay,
                        ),
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      RangeSlider(
                        values: RangeValues(
                          settings.minDelay.toDouble(),
                          settings.maxDelay.toDouble(),
                        ),
                        min: 1,
                        max: 60,
                        divisions: 59,
                        activeColor: colorScheme.primary,
                        labels: RangeLabels(
                          '${settings.minDelay}s',
                          '${settings.maxDelay}s',
                        ),
                        onChanged: (val) {
                          ref
                              .read(settingsProvider.notifier)
                              .updateSettings(
                                settings.copyWith(
                                  minDelay: val.start.toInt(),
                                  maxDelay: val.end.toInt(),
                                ),
                              );
                        },
                      ),
                    ],
                  ),
                ),
                _buildTextFieldTile(
                  colorScheme: colorScheme,
                  label: l10n.dailyTransmissionLimit,
                  initialValue: settings.dailyLimit.toString(),
                  onChanged: (val) {
                    final limit = int.tryParse(val) ?? 500;
                    ref
                        .read(settingsProvider.notifier)
                        .updateSettings(settings.copyWith(dailyLimit: limit));
                  },
                ),
              ],
            ),

            const SizedBox(height: 32),

            // 4. PERSONA ENGINE (AI)
            _buildSectionHeader(
              l10n.aiPersonaEngine.toUpperCase(),
              colorScheme,
            ),
            _buildSettingsCard(
              colorScheme,
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 16,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            l10n.creativityThreshold,
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            settings.aiCreativity.toStringAsFixed(2),
                            style: TextStyle(
                              color: colorScheme.primary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      Slider(
                        value: settings.aiCreativity,
                        min: 0,
                        max: 1,
                        activeColor: colorScheme.primary,
                        onChanged: (val) {
                          ref
                              .read(settingsProvider.notifier)
                              .updateSettings(
                                settings.copyWith(aiCreativity: val),
                              );
                        },
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              '(منطقي/دقيق)',
                              style: TextStyle(
                                fontSize: 10,
                                color: colorScheme.onSurface.withValues(
                                  alpha: 0.5,
                                ),
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              '(إبداعي/حر)',
                              style: TextStyle(
                                fontSize: 10,
                                color: colorScheme.onSurface.withValues(
                                  alpha: 0.5,
                                ),
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 32),
            _buildUpdateCenter(context, ref, colorScheme, l10n),

            const SizedBox(height: 48),

            Center(
              child: Text(
                "${l10n.osVersion.toUpperCase()} | v${settings.version}",
                style: TextStyle(
                  fontSize: 10,
                  color: colorScheme.onSurface.withValues(alpha: 0.3),
                  letterSpacing: 2,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildUpdateCenter(
    BuildContext context,
    WidgetRef ref,
    ColorScheme colorScheme,
    AppLocalizations l10n,
  ) {
    final updateState = ref.watch(updateControllerProvider);
    final notifier = ref.read(updateControllerProvider.notifier);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader("SYSTEM UPDATE HUB", colorScheme),
        _buildSettingsCard(
          colorScheme,
          children: [
            ListTile(
              leading: Icon(
                Icons.system_update_rounded,
                color: updateState.updateInfo?.hasUpdate == true
                    ? colorScheme.statusWarning
                    : colorScheme.primary,
              ),
              title: Text(
                updateState.updateInfo?.hasUpdate == true
                    ? "UPDATE DISCOVERED: v${updateState.updateInfo!.latestVersion}"
                    : "ALL SYSTEMS OPTIMAL",
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                ),
              ),
              subtitle: Text(
                updateState.updateInfo?.hasUpdate == true
                    ? "New biological patterns and architectural fixes available."
                    : "You are running the most advanced localized version.",
                style: const TextStyle(fontSize: 11),
              ),
              trailing: updateState.isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : TextButton(
                      onPressed: notifier.checkForUpdates,
                      child: const Text("CHECK"),
                    ),
            ),
            if (updateState.updateInfo?.hasUpdate == true)
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: colorScheme.surfaceContainerHighest.withValues(
                          alpha: 0.5,
                        ),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: colorScheme.statusWarning.withValues(
                            alpha: 0.3,
                          ),
                        ),
                      ),
                      child: SelectableText(
                        updateState.updateInfo!.changelog ??
                            "No changelog provided.",
                        style: TextStyle(
                          fontSize: 10,
                          fontFamily: 'monospace',
                          color: colorScheme.onSurface.withValues(alpha: 0.7),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton.icon(
                        onPressed: updateState.isApplying
                            ? null
                            : notifier.applyUpdate,
                        icon: updateState.isApplying
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Icon(Icons.download_for_offline_rounded),
                        label: Text(
                          updateState.isApplying
                              ? "APPLYING PATCH..."
                              : "UPGRADE PROTOCOL",
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1.2,
                          ),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: colorScheme.statusWarning,
                          foregroundColor: Colors.black,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            if (updateState.error != null)
              Padding(
                padding: const EdgeInsets.all(12),
                child: Text(
                  "ERROR: ${updateState.error}",
                  style: TextStyle(color: colorScheme.error, fontSize: 10),
                ),
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildSectionHeader(String title, ColorScheme colors) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, left: 4),
      child: Text(
        title,
        style: TextStyle(
          color: colors.primary,
          fontWeight: FontWeight.w900,
          letterSpacing: 2,
          fontSize: 11,
          fontFamily: 'Oxanium',
        ),
      ),
    );
  }

  Widget _buildSettingsCard(
    ColorScheme colors, {
    required List<Widget> children,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: colors.surfaceContainer,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: colors.primary.withValues(alpha: 0.1)),
      ),
      child: Column(children: children),
    );
  }

  Widget _buildDropdownTile<T>({
    required String label,
    required T value,
    required List<T> items,
    required ValueChanged<T?> onChanged,
  }) {
    return ListTile(
      title: Text(
        label,
        style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
      ),
      trailing: DropdownButton<T>(
        value: value,
        underline: const SizedBox(),
        items: items
            .map(
              (e) => DropdownMenuItem<T>(
                value: e,
                child: Text(
                  e is Enum ? e.name.toUpperCase() : e.toString(),
                  style: const TextStyle(fontSize: 12),
                ),
              ),
            )
            .toList(),
        onChanged: onChanged,
      ),
    );
  }

  Widget _buildTextFieldTile({
    required ColorScheme colorScheme,
    required String label,
    required String initialValue,
    required ValueChanged<String> onChanged,
    bool isPassword = false,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: TextFormField(
        initialValue: initialValue,
        obscureText: isPassword,
        style: const TextStyle(fontSize: 13, fontFamily: 'monospace'),
        decoration: InputDecoration(
          labelText: label,
          labelStyle: TextStyle(
            fontSize: 10,
            letterSpacing: 1,
            color: colorScheme.onSurface.withValues(alpha: 0.5),
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(
              color: colorScheme.outline.withValues(alpha: 0.2),
            ),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(
              color: colorScheme.outline.withValues(alpha: 0.1),
            ),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide(color: colorScheme.primary, width: 2),
          ),
        ),
        onChanged: onChanged,
      ),
    );
  }
}

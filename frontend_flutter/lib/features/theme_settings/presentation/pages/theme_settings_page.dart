import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/theme/theme_controller.dart';
import 'package:g777_client/shared/providers/theme_provider.dart';

class ThemeSettingsPage extends ConsumerWidget {
  const ThemeSettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeController = ThemeController(ref);
    final currentStyle = ref.watch(themeStyleProvider);
    final currentMode = ref.watch(themeModeProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Theme Settings')),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          const Text(
            'Visual Style Configuration',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 32),
          ListTile(
            title: const Text('Brightness Mode'),
            trailing: Switch(
              value: currentMode.flutterThemeMode == ThemeMode.dark,
              onChanged: (v) => themeController.toggleThemeMode(),
            ),
          ),
          const Divider(),
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 16.0),
            child: Text(
              'Style Presets',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 8),
          Center(
            child: SegmentedButton<ThemeStyle>(
              segments: const [
                ButtonSegment(
                  value: ThemeStyle.neon,
                  label: Text('NEON'),
                  icon: Icon(Icons.bolt, size: 16),
                ),
                ButtonSegment(
                  value: ThemeStyle.professional,
                  label: Text('PRO'),
                  icon: Icon(Icons.business, size: 16),
                ),
                ButtonSegment(
                  value: ThemeStyle.industrial,
                  label: Text('IND'),
                  icon: Icon(Icons.precision_manufacturing, size: 16),
                ),
                ButtonSegment(
                  value: ThemeStyle.modernGlass,
                  label: Text('GLASS'),
                  icon: Icon(Icons.blur_on, size: 16),
                ),
              ],
              selected: {currentStyle},
              onSelectionChanged: (Set<ThemeStyle> newSelection) {
                themeController.setThemeStyle(newSelection.first);
              },
              showSelectedIcon: false,
            ),
          ),
        ],
      ),
    );
  }
}

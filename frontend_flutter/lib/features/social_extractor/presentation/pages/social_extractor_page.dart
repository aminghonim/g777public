import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/theme/semantic_colors.dart';
import 'package:g777_client/core/theme/theme_extensions.dart';

import '../providers/social_extractor_provider.dart';

class SocialExtractorPage extends ConsumerStatefulWidget {
  const SocialExtractorPage({super.key});

  @override
  ConsumerState<SocialExtractorPage> createState() =>
      _SocialExtractorPageState();
}

class _SocialExtractorPageState extends ConsumerState<SocialExtractorPage> {
  final _keywordController = TextEditingController();

  @override
  void dispose() {
    _keywordController.dispose();
    super.dispose();
  }

  Future<void> _triggerScan() async {
    if (_keywordController.text.isEmpty) {
      return;
    }
    await ref
        .read(socialExtractorProvider.notifier)
        .triggerScan(_keywordController.text);
  }

  Future<void> _exportResults(List<Map<String, dynamic>> results) async {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Exporting ${results.length} results...'),
        backgroundColor: Theme.of(context).colorScheme.primary,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // ignore: unused_local_variable - reserved for future i18n usage
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final themeExt = theme.extension<G777ThemeExtension>();
    final state = ref.watch(socialExtractorProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(colorScheme),
          const SizedBox(height: 32),
          _buildSearchCard(colorScheme, themeExt, state),
          const SizedBox(height: 24),
          if (state.isScanning || state.logs.isNotEmpty)
            _buildLogConsole(colorScheme, themeExt, state),
          if (state.error != null) _buildErrorCard(colorScheme, state.error!),
          if (state.results.isNotEmpty) ...[
            const SizedBox(height: 24),
            _buildResultsSection(colorScheme, themeExt, state.results),
          ],
        ],
      ),
    );
  }

  Widget _buildHeader(ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'SOCIAL MEDIA EXTRACTOR',
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            letterSpacing: 2,
            fontFamily: 'Oxanium',
            color: colorScheme.secondary,
            shadows: [
              Shadow(
                color: colorScheme.secondary.withValues(alpha: 0.5),
                blurRadius: 15,
              ),
            ],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Extract leads from social media platforms based on keywords.',
          style: TextStyle(
            color: colorScheme.onSurfaceVariant,
            fontSize: 12,
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }

  Widget _buildSearchCard(
    ColorScheme colorScheme,
    G777ThemeExtension? themeExt,
    SocialExtractorState state,
  ) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(themeExt?.edgeRadius ?? 16),
        border: Border.all(color: colorScheme.secondary.withValues(alpha: 0.3)),
        boxShadow: [
          BoxShadow(
            color: (themeExt?.glowColor ?? colorScheme.secondary).withValues(
              alpha: themeExt?.glowIntensity ?? 0.05,
            ),
            blurRadius: themeExt?.glassBlur ?? 10,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildPlatformSelector(colorScheme, state),
          const SizedBox(height: 16),
          _buildTextField(
            label: 'SEARCH KEYWORD',
            hint: 'e.g. Digital Marketing, Real Estate, Fitness Coach',
            controller: _keywordController,
            colorScheme: colorScheme,
            icon: Icons.search,
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            height: 54,
            child: ElevatedButton.icon(
              onPressed: state.isScanning ? null : _triggerScan,
              icon: state.isScanning
                  ? SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: colorScheme.onSecondary,
                      ),
                    )
                  : const Icon(Icons.radar, size: 20),
              label: Text(
                state.isScanning ? 'SCANNING...' : 'START EXTRACTION',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                  fontFamily: 'Oxanium',
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: colorScheme.secondary,
                foregroundColor: colorScheme.onSecondary,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlatformSelector(
    ColorScheme colorScheme,
    SocialExtractorState state,
  ) {
    final platforms = [
      {'id': 'all', 'name': 'ALL PLATFORMS', 'icon': Icons.public},
      {'id': 'facebook', 'name': 'FACEBOOK', 'icon': Icons.facebook},
      {'id': 'instagram', 'name': 'INSTAGRAM', 'icon': Icons.camera_alt},
      {'id': 'linkedin', 'name': 'LINKEDIN', 'icon': Icons.business},
      {'id': 'twitter', 'name': 'TWITTER', 'icon': Icons.chat},
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'SELECT PLATFORM',
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.5,
            color: colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: platforms.map((platform) {
            final isSelected = state.selectedPlatform == platform['id'];
            return ChoiceChip(
              label: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    platform['icon'] as IconData,
                    size: 14,
                    color: isSelected
                        ? colorScheme.onSecondary
                        : colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(width: 6),
                  Text(platform['name'] as String),
                ],
              ),
              selected: isSelected,
              onSelected: (_) => ref
                  .read(socialExtractorProvider.notifier)
                  .setPlatform(platform['id'] as String),
              selectedColor: colorScheme.secondary,
              backgroundColor: colorScheme.surfaceContainerHighest,
              labelStyle: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                color: isSelected
                    ? colorScheme.onSecondary
                    : colorScheme.onSurfaceVariant,
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildTextField({
    required String label,
    required String hint,
    required TextEditingController controller,
    required ColorScheme colorScheme,
    required IconData icon,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.5,
            color: colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: TextStyle(
              color: colorScheme.outline.withValues(alpha: 0.5),
            ),
            prefixIcon: Icon(icon, size: 18, color: colorScheme.secondary),
            filled: true,
            fillColor: colorScheme.surfaceContainerHighest,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: colorScheme.outline.withValues(alpha: 0.3),
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: colorScheme.outline.withValues(alpha: 0.3),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildLogConsole(
    ColorScheme colorScheme,
    G777ThemeExtension? themeExt,
    SocialExtractorState state,
  ) {
    return Container(
      height: 250,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(themeExt?.edgeRadius ?? 12),
        border: Border.all(color: colorScheme.secondary.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'EXTRACTION LOGS',
                style: TextStyle(
                  color: colorScheme.secondary,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                ),
              ),
              if (state.logs.isNotEmpty)
                TextButton.icon(
                  onPressed: () =>
                      ref.read(socialExtractorProvider.notifier).clearLogs(),
                  icon: Icon(
                    Icons.clear_all,
                    size: 14,
                    color: colorScheme.onSurfaceVariant,
                  ),
                  label: Text(
                    'CLEAR',
                    style: TextStyle(
                      fontSize: 10,
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Divider(color: colorScheme.outline.withValues(alpha: 0.3), height: 1),
          const SizedBox(height: 8),
          Expanded(
            child: state.logs.isEmpty
                ? Center(
                    child: Text(
                      'WAITING FOR EXTRACTION...',
                      style: TextStyle(
                        color: colorScheme.outline.withValues(alpha: 0.5),
                        fontSize: 10,
                        letterSpacing: 2,
                      ),
                    ),
                  )
                : ListView.builder(
                    reverse: true,
                    itemCount: state.logs.length,
                    itemBuilder: (context, index) {
                      final log = state.logs[index];
                      final isError = log.contains('[ERROR]');
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Text(
                          log,
                          style: TextStyle(
                            fontFamily: 'monospace',
                            fontSize: 11,
                            color: isError
                                ? colorScheme.statusError
                                : colorScheme.onSurface,
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorCard(ColorScheme colorScheme, String error) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.statusError.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: colorScheme.statusError.withValues(alpha: 0.3),
        ),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: colorScheme.statusError),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              error,
              style: TextStyle(color: colorScheme.statusError),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 18),
            onPressed: () =>
                ref.read(socialExtractorProvider.notifier).clearError(),
          ),
        ],
      ),
    );
  }

  Widget _buildResultsSection(
    ColorScheme colorScheme,
    G777ThemeExtension? themeExt,
    List<Map<String, dynamic>> results,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'SCAN RESULTS',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
                color: colorScheme.secondary,
              ),
            ),
            ElevatedButton.icon(
              onPressed: () => _exportResults(results),
              icon: const Icon(Icons.download, size: 16),
              label: const Text('EXPORT CSV'),
              style: ElevatedButton.styleFrom(
                backgroundColor: colorScheme.statusOnline.withValues(
                  alpha: 0.1,
                ),
                foregroundColor: colorScheme.statusOnline,
                side: BorderSide(color: colorScheme.statusOnline),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: results.take(20).length,
          separatorBuilder: (_, _) => Divider(
            color: colorScheme.outline.withValues(alpha: 0.2),
            height: 1,
          ),
          itemBuilder: (context, index) {
            final item = results[index];
            return ListTile(
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 8,
              ),
              leading: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: colorScheme.secondary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  _getPlatformIcon(item['platform']?.toString()),
                  color: colorScheme.secondary,
                  size: 20,
                ),
              ),
              title: Text(
                item['name']?.toString() ?? 'Unknown',
                style: TextStyle(
                  color: colorScheme.onSurface,
                  fontWeight: FontWeight.bold,
                ),
              ),
              subtitle: Text(
                item['profile_url']?.toString() ?? 'N/A',
                style: TextStyle(
                  color: colorScheme.onSurfaceVariant,
                  fontSize: 12,
                  fontFamily: 'monospace',
                ),
              ),
              trailing: IconButton(
                icon: Icon(
                  Icons.open_in_new,
                  color: colorScheme.primary,
                  size: 18,
                ),
                onPressed: () {
                  // Open profile URL
                },
              ),
            );
          },
        ),
      ],
    );
  }

  IconData _getPlatformIcon(String? platform) {
    switch (platform?.toLowerCase()) {
      case 'facebook':
        return Icons.facebook;
      case 'instagram':
        return Icons.camera_alt;
      case 'linkedin':
        return Icons.business;
      case 'twitter':
        return Icons.chat;
      default:
        return Icons.person;
    }
  }
}

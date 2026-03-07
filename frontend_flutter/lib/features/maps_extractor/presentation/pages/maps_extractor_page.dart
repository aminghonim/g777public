import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/theme/semantic_colors.dart';
import 'package:g777_client/core/theme/theme_extensions.dart';

import '../providers/maps_extractor_provider.dart';

class MapsExtractorPage extends ConsumerStatefulWidget {
  const MapsExtractorPage({super.key});

  @override
  ConsumerState<MapsExtractorPage> createState() => _MapsExtractorPageState();
}

class _MapsExtractorPageState extends ConsumerState<MapsExtractorPage> {
  final _queryController = TextEditingController();
  final _locationController = TextEditingController(text: 'Cairo, Egypt');

  @override
  void dispose() {
    _queryController.dispose();
    _locationController.dispose();
    super.dispose();
  }

  Future<void> _triggerScan() async {
    if (_queryController.text.isEmpty || _locationController.text.isEmpty) {
      return;
    }
    await ref
        .read(mapsExtractorProvider.notifier)
        .triggerScan(_queryController.text, _locationController.text);
  }

  Future<void> _exportResults(List<Map<String, dynamic>> results) async {
    // TODO: Implement export functionality
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
    final state = ref.watch(mapsExtractorProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(colorScheme),
          const SizedBox(height: 32),
          _buildSearchCard(colorScheme, themeExt, state),
          const SizedBox(height: 24),
          if (state.isScanning) _buildProgressIndicator(colorScheme),
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
          'GOOGLE MAPS EXTRACTOR',
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            letterSpacing: 2,
            fontFamily: 'Oxanium',
            color: colorScheme.primary,
            shadows: [
              Shadow(
                color: colorScheme.primary.withValues(alpha: 0.5),
                blurRadius: 15,
              ),
            ],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Extract business data from Google Maps for targeted outreach.',
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
    MapsExtractorState state,
  ) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(themeExt?.edgeRadius ?? 16),
        border: Border.all(color: colorScheme.primary.withValues(alpha: 0.3)),
        boxShadow: [
          BoxShadow(
            color: (themeExt?.glowColor ?? colorScheme.primary).withValues(
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
          Row(
            children: [
              Expanded(
                child: _buildTextField(
                  label: 'BUSINESS TYPE',
                  hint: 'e.g. Restaurants, Hotels, Clinics',
                  controller: _queryController,
                  colorScheme: colorScheme,
                  icon: Icons.business,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildTextField(
                  label: 'LOCATION',
                  hint: 'e.g. Cairo, Egypt',
                  controller: _locationController,
                  colorScheme: colorScheme,
                  icon: Icons.location_on,
                ),
              ),
            ],
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
                        color: colorScheme.onPrimary,
                      ),
                    )
                  : const Icon(Icons.search, size: 20),
              label: Text(
                state.isScanning ? 'SCANNING...' : 'START EXTRACTION',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                  fontFamily: 'Oxanium',
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: colorScheme.primary,
                foregroundColor: colorScheme.onPrimary,
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
            prefixIcon: Icon(icon, size: 18, color: colorScheme.primary),
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

  Widget _buildProgressIndicator(ColorScheme colorScheme) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: colorScheme.statusWarning.withValues(alpha: 0.3),
        ),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: colorScheme.statusWarning,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Scanning Google Maps...',
                  style: TextStyle(
                    color: colorScheme.onSurface,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'This may take 1-2 minutes depending on results count',
                  style: TextStyle(
                    color: colorScheme.onSurfaceVariant,
                    fontSize: 12,
                  ),
                ),
              ],
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
                ref.read(mapsExtractorProvider.notifier).clearError(),
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
                color: colorScheme.primary,
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
        Container(
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainer,
            borderRadius: BorderRadius.circular(themeExt?.edgeRadius ?? 16),
            border: Border.all(
              color: colorScheme.outline.withValues(alpha: 0.2),
            ),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(themeExt?.edgeRadius ?? 16),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                headingRowColor: WidgetStatePropertyAll(
                  colorScheme.surfaceContainerHighest,
                ),
                columns: [
                  DataColumn(
                    label: Text(
                      'BUSINESS NAME',
                      style: TextStyle(
                        color: colorScheme.onSurfaceVariant,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                  ),
                  DataColumn(
                    label: Text(
                      'PHONE',
                      style: TextStyle(
                        color: colorScheme.onSurfaceVariant,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                  ),
                  DataColumn(
                    label: Text(
                      'ADDRESS',
                      style: TextStyle(
                        color: colorScheme.onSurfaceVariant,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                  ),
                  DataColumn(
                    label: Text(
                      'RATING',
                      style: TextStyle(
                        color: colorScheme.onSurfaceVariant,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                  ),
                ],
                rows: results.take(50).map((item) {
                  return DataRow(
                    cells: [
                      DataCell(
                        Text(
                          item['name']?.toString() ?? 'N/A',
                          style: TextStyle(color: colorScheme.onSurface),
                        ),
                      ),
                      DataCell(
                        Text(
                          item['phone']?.toString() ?? 'N/A',
                          style: TextStyle(
                            color: colorScheme.primary,
                            fontFamily: 'monospace',
                          ),
                        ),
                      ),
                      DataCell(
                        Text(
                          item['address']?.toString() ?? 'N/A',
                          style: TextStyle(color: colorScheme.onSurfaceVariant),
                        ),
                      ),
                      DataCell(
                        Row(
                          children: [
                            Icon(
                              Icons.star,
                              size: 14,
                              color: colorScheme.statusWarning,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              item['rating']?.toString() ?? 'N/A',
                              style: TextStyle(color: colorScheme.onSurface),
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                }).toList(),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

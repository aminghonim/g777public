import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/api_service.dart';
import 'package:g777_client/core/theme/semantic_colors.dart';
import 'package:g777_client/core/theme/theme_extensions.dart';
import 'package:g777_client/shared/providers/logs_provider.dart';

class GroupFinderPage extends ConsumerStatefulWidget {
  const GroupFinderPage({super.key});

  @override
  ConsumerState<GroupFinderPage> createState() => _GroupFinderPageState();
}

class _GroupFinderPageState extends ConsumerState<GroupFinderPage> {
  final ApiService _api = ApiService();
  final _keywordController = TextEditingController();
  final _countryController = TextEditingController();
  bool _isSearching = false;
  List<String> _results = [];
  String? _error;

  @override
  void dispose() {
    _keywordController.dispose();
    _countryController.dispose();
    super.dispose();
  }

  Future<void> _startSearch() async {
    if (_keywordController.text.isEmpty) return;

    setState(() {
      _isSearching = true;
      _error = null;
      _results = [];
    });

    try {
      final response = await _api.triggerScan(
        type: 'group',
        keyword: _keywordController.text,
        country: _countryController.text,
      );

      // Poll for results after a delay
      await Future.delayed(const Duration(seconds: 5));
      final oppData = await _api.getOpportunities(source: 'group');
      final dataResults = (oppData['results'] as List?) ?? [];

      if (mounted) {
        setState(() {
          _isSearching = false;
          if (dataResults.isNotEmpty) {
            _results = dataResults
                .where(
                  (r) =>
                      r is Map &&
                      (r.containsKey('link') || r.containsKey('url')),
                )
                .map((r) => (r['link'] ?? r['url'] ?? '').toString())
                .where((link) => link.isNotEmpty)
                .toList();
          }
        });
      }

      ref
          .read(logsProvider.notifier)
          .addLog(
            'Group Finder: Found ${_results.length} groups for "${_keywordController.text}"',
          );
    } catch (e) {
      if (mounted) {
        setState(() {
          _isSearching = false;
          _error = e.toString();
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final themeExt = theme.extension<G777ThemeExtension>();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(colorScheme),
          const SizedBox(height: 32),
          _buildSearchCard(colorScheme, themeExt),
          const SizedBox(height: 24),
          if (_isSearching) _buildProgressIndicator(colorScheme),
          if (_error != null) _buildErrorCard(colorScheme),
          if (_results.isNotEmpty) ...[
            const SizedBox(height: 24),
            _buildResultsSection(colorScheme, themeExt),
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
          'GROUP FINDER',
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: colorScheme.primary,
            letterSpacing: 2,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Discover WhatsApp groups using ScraplingEngine + AI Self-Healing',
          style: TextStyle(fontSize: 14, color: colorScheme.onSurfaceVariant),
        ),
      ],
    );
  }

  Widget _buildSearchCard(
    ColorScheme colorScheme,
    G777ThemeExtension? themeExt,
  ) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Search Parameters',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: colorScheme.primary,
              ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _keywordController,
              decoration: InputDecoration(
                labelText: 'Keyword',
                hintText: 'e.g., travel agencies, restaurants, marketing',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _countryController,
              decoration: InputDecoration(
                labelText: 'Country (optional)',
                hintText: 'e.g., Egypt, Saudi Arabia',
                prefixIcon: const Icon(Icons.public),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: FilledButton.icon(
                onPressed: _isSearching ? null : _startSearch,
                icon: _isSearching
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.explore),
                label: Text(
                  _isSearching ? 'Searching...' : 'Find Groups',
                  style: const TextStyle(fontSize: 16),
                ),
                style: FilledButton.styleFrom(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressIndicator(ColorScheme colorScheme) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            CircularProgressIndicator(color: colorScheme.primary),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Searching for groups...',
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: colorScheme.onSurface,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'ScraplingEngine is fetching and analyzing results',
                    style: TextStyle(
                      fontSize: 12,
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorCard(ColorScheme colorScheme) {
    return Card(
      elevation: 2,
      color: colorScheme.errorContainer,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.error_outline, color: colorScheme.error),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                _error ?? 'Unknown error',
                style: TextStyle(color: colorScheme.onErrorContainer),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultsSection(
    ColorScheme colorScheme,
    G777ThemeExtension? themeExt,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Found ${_results.length} Groups',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: colorScheme.primary,
              ),
            ),
            FilledButton.tonalIcon(
              onPressed: () {
                // TODO: Export results
              },
              icon: const Icon(Icons.download),
              label: const Text('Export'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        ..._results.map((link) => _buildResultItem(link, colorScheme)),
      ],
    );
  }

  Widget _buildResultItem(String link, ColorScheme colorScheme) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: ListTile(
        leading: Icon(Icons.group, color: colorScheme.primary),
        title: Text(
          link,
          style: const TextStyle(fontSize: 13),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: IconButton(
          icon: const Icon(Icons.copy, size: 18),
          onPressed: () {
            // TODO: Copy to clipboard
          },
        ),
      ),
    );
  }
}

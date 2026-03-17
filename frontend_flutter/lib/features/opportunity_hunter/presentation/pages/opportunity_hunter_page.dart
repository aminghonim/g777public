import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/api_service.dart';
import 'package:g777_client/l10n/app_localizations.dart';
// Note: Some imports might be needed for the actual app context
import 'package:g777_client/core/providers/system_stream_provider.dart';
import 'package:g777_client/shared/providers/logs_provider.dart';
import 'package:g777_client/core/theme/theme.dart';

class OpportunityHunterPage extends ConsumerStatefulWidget {
  const OpportunityHunterPage({super.key});

  @override
  ConsumerState<OpportunityHunterPage> createState() =>
      _OpportunityHunterPageState();
}

class _OpportunityHunterPageState extends ConsumerState<OpportunityHunterPage> {
  final ApiService _api = ApiService();
  final _keywordController = TextEditingController();
  final String _selectedSource = 'social'; // Fixed to social
  bool _isScanning = false;
  bool _isLoadingData = false;
  List<dynamic> _opportunities = [];
  int _scrollingDepth = 2;
  String _latestLog = "Idle - Waiting for scan...";

  @override
  void initState() {
    super.initState();
    _fetchOpportunities();
  }

  @override
  void dispose() {
    _keywordController.dispose();
    super.dispose();
  }

  String _sanitizeKeyword(String raw) {
    final trimmed = raw.trim();
    if (trimmed.isEmpty) return '';

    final cleaned = trimmed.replaceAll(
      RegExp(r'[^a-zA-Z0-9\u0600-\u06FF\s,.\-_/]'),
      '',
    );
    final normalizedSpaces = cleaned.replaceAll(RegExp(r'\s+'), ' ');
    return normalizedSpaces.trim();
  }

  Future<void> _fetchOpportunities() async {
    if (!mounted) return;
    setState(() => _isLoadingData = true);
    try {
      final response = await _api.getOpportunities(limit: 50);
      setState(() {
        _opportunities = response['results'] ?? [];
      });
    } catch (e) {
      final notifier = ref.read(logsProvider.notifier);
      notifier.addLog('Opportunity fetch failed: $e', type: LogType.error);
    } finally {
      if (mounted) setState(() => _isLoadingData = false);
    }
  }

  Future<void> _startScan() async {
    final notifier = ref.read(logsProvider.notifier);
    final theme = Theme.of(context);
    final colors = theme.colorScheme;

    final sanitized = _sanitizeKeyword(_keywordController.text);
    if (sanitized.isEmpty) {
      notifier.addLog('Keyword required for scan', type: LogType.error);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Please enter a valid discovery keyword.'),
            backgroundColor: colors.statusError,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
      return;
    }

    _keywordController.text = sanitized;

    setState(() => _isScanning = true);
    notifier.addLog(
      'Launching social scan for: "$sanitized"',
      type: LogType.info,
    );

    try {
      await _api.triggerScan(
        type: _selectedSource,
        keyword: sanitized,
        scrollingDepth: _scrollingDepth,
      );
      notifier.addLog(
        'Scan job initiated. Depth: $_scrollingDepth. Results will populate automatically.',
        type: LogType.success,
      );
    } catch (e) {
      notifier.addLog('Scan failed: $e', type: LogType.error);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Scan failed. Please try again.'),
            backgroundColor: colors.statusError,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isScanning = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(l10n, theme),
          const SizedBox(height: 32),
          _buildScannerConfig(l10n, theme, isDark),
          const SizedBox(height: 16),
          _buildLiveProgress(theme, isDark),
          const SizedBox(height: 24),
          _buildResultsHeader(l10n, theme),
          const SizedBox(height: 16),
          _buildResultsList(theme, isDark),
        ],
      ),
    );
  }

  Widget _buildLiveProgress(ThemeData theme, bool isDark) {
    final colors = theme.colorScheme;
    final accent = colors.grabberAccent;
    ref.listen(campaignStreamProvider, (prev, next) {
      next.whenData((event) {
        if (event['type'] == 'LOG') {
          final logData = event['data'];
          if (logData != null && logData['message'] != null) {
            setState(() {
              _latestLog = logData['message'];
            });
          }
        }
      });
    });

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: colors.surfaceContainerHighest.withValues(
          alpha: isDark ? 0.25 : 0.7,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: accent.withValues(alpha: 0.15)),
      ),
      child: Row(
        children: [
          Icon(Icons.terminal, size: 14, color: accent),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _latestLog,
              style: TextStyle(
                fontFamily: 'monospace',
                fontSize: 11,
                color: colors.onSurface.withValues(alpha: 0.65),
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          if (_isScanning)
            SizedBox(
              width: 12,
              height: 12,
              child: CircularProgressIndicator(
                strokeWidth: 1,
                color: accent,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildHeader(AppLocalizations l10n, ThemeData theme) {
    final colors = theme.colorScheme;
    final accent = colors.grabberAccent;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.travel_explore, color: accent, size: 32),
            const SizedBox(width: 12),
            const Text(
              "OPPORTUNITY HUNTER",
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Colors.pinkAccent, // Pink for social
                letterSpacing: 2,
                fontFamily: 'Oxanium',
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          "AI-Powered Social Media Intelligence Engine",
          style: TextStyle(
            color: colors.onSurface.withValues(alpha: 0.5),
            fontSize: 12,
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }

  Widget _buildScannerConfig(
    AppLocalizations l10n,
    ThemeData theme,
    bool isDark,
  ) {
    final colors = theme.colorScheme;
    final accent = Colors.pinkAccent; // Pink for social
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colors.grabberCardBackground.withValues(
          alpha: isDark ? 0.9 : 1.0,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: accent.withValues(alpha: 0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "SOCIAL DISCOVERY",
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.5,
              color: accent,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                flex: 2,
                child: TextField(
                  controller: _keywordController,
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
                  decoration: InputDecoration(
                    hintText: 'Search Keyword (e.g. Real Estate Dubai)',
                    hintStyle: TextStyle(color: colors.inputPlaceholder),
                    filled: true,
                    fillColor: colors.inputBackground,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide.none,
                    ),
                    prefixIcon: Icon(
                      Icons.search,
                      color: colors.onSurface.withValues(alpha: 0.35),
                      size: 18,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              ElevatedButton.icon(
                onPressed: _isScanning ? null : _startScan,
                icon: _isScanning
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.radar, size: 18),
                label: const Text("START SCAN"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: accent,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 18,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Icon(Icons.unfold_more, size: 14, color: accent),
              const SizedBox(width: 8),
              Text(
                "SCROLLING DEPTH:",
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  color: colors.onSurface.withValues(alpha: 0.45),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Slider(
                  value: _scrollingDepth.toDouble(),
                  min: 1,
                  max: 10,
                  divisions: 9,
                  label: _scrollingDepth.toString(),
                  activeColor: accent,
                  onChanged: (v) =>
                      setState(() => _scrollingDepth = v.toInt()),
                ),
              ),
              const SizedBox(width: 12),
              Text(
                "$_scrollingDepth pages",
                style: TextStyle(
                  fontSize: 11,
                  fontFamily: 'monospace',
                  color: accent,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildResultsHeader(AppLocalizations l10n, ThemeData theme) {
    const accent = Colors.pinkAccent;
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          "RESULTS (${_opportunities.length})",
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.5,
          ),
        ),
        IconButton(
          onPressed: _fetchOpportunities,
          icon: _isLoadingData
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : Icon(Icons.refresh, color: accent),
          tooltip: 'Refresh Results',
        ),
      ],
    );
  }

  Widget _buildResultsList(ThemeData theme, bool isDark) {
    final colors = theme.colorScheme;
    if (_opportunities.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(48.0),
          child: Text(
            'No opportunities found yet.\nStart a scan above.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: colors.onSurface.withValues(alpha: 0.3),
              height: 1.5,
            ),
          ),
        ),
      );
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: _opportunities.length,
      itemBuilder: (context, index) {
        final item = _opportunities[index];
        const sourceIcon = Icons.public;
        const sourceColor = Colors.pinkAccent;

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: colors.surfaceContainerHighest.withValues(
              alpha: isDark ? 0.12 : 0.6,
            ),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: colors.outline.withValues(alpha: 0.12)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: sourceColor.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  sourceIcon,
                  color: sourceColor,
                  size: 20,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item['name'] ?? 'Unknown Lead',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          Icons.phone,
                          size: 12,
                          color: colors.statusOnline,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          item['phone'] ?? 'No Phone',
                          style: TextStyle(
                            fontFamily: 'monospace',
                            fontSize: 12,
                            color: colors.onSurface.withValues(alpha: 0.8),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    item['_scraped_at']?.toString().split('T')[0] ?? '',
                    style: TextStyle(
                      fontSize: 10,
                      color: colors.onSurface.withValues(alpha: 0.35),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}

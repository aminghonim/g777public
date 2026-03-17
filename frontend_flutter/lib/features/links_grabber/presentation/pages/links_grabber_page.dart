import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/api_service.dart';
import 'package:g777_client/shared/providers/logs_provider.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:excel/excel.dart' as xl;
import 'package:g777_client/core/theme/theme.dart'; // Unified theme system

class LinksGrabberPage extends ConsumerStatefulWidget {
  const LinksGrabberPage({super.key});

  @override
  ConsumerState<LinksGrabberPage> createState() => _LinksGrabberPageState();
}

class _LinksGrabberPageState extends ConsumerState<LinksGrabberPage> {
  final ApiService _api = ApiService();
  final _keywordController = TextEditingController();
  int _count = 10;
  bool _isHunting = false;
  List<dynamic> _results = [];

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

  Future<void> _startHunt() async {
    final notifier = ref.read(logsProvider.notifier);
    final colorScheme = Theme.of(context).colorScheme;

    final sanitized = _sanitizeKeyword(_keywordController.text);
    if (sanitized.isEmpty) {
      notifier.addLog('Search keyword is required.', type: LogType.error);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Please enter a valid search keyword.'),
            backgroundColor: colorScheme.statusError,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
      return;
    }

    _keywordController.text = sanitized;

    setState(() {
      _isHunting = true;
      _results = [];
    });

    notifier.addLog(
      'Initiating Link Hunt for keyword: $sanitized',
      type: LogType.info,
    );

    try {
      final response = await _api.startLinkHunt(
        keyword: sanitized,
        count: _count,
      );

      setState(() {
        final links = List<String>.from(response['links'] ?? []);
        _results = links
            .map((link) => {'title': 'WhatsApp Group', 'link': link})
            .toList();
      });

      notifier.addLog(
        'Hunt complete. Found ${_results.length} groups.',
        type: LogType.success,
      );
    } catch (e) {
      notifier.addLog('Hunt failed: $e', type: LogType.error);
    } finally {
      setState(() => _isHunting = false);
    }
  }

  Future<void> _exportResults() async {
    if (_results.isEmpty) return;
    final notifier = ref.read(logsProvider.notifier);
    final colorScheme = Theme.of(context).colorScheme;

    try {
      final excel = xl.Excel.createExcel();
      final sheet = excel['Links'];
      sheet.appendRow([xl.TextCellValue('Index'), xl.TextCellValue('Link')]);
      for (int i = 0; i < _results.length; i++) {
        sheet.appendRow([
          xl.IntCellValue(i + 1),
          xl.TextCellValue(_results[i]['link']?.toString() ?? ''),
        ]);
      }
      final downloadsPath =
          '${Platform.environment['USERPROFILE'] ?? Platform.environment['HOME']}/Downloads';
      final filePath =
          '$downloadsPath/g777_links_${DateTime.now().millisecondsSinceEpoch}.xlsx';
      final bytes = excel.encode();
      if (bytes != null) {
        await File(filePath).writeAsBytes(bytes);
        notifier.addLog('Export saved: $filePath', type: LogType.success);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'EXPORTED ${_results.length} LINKS',
                style: TextStyle(
                  color: colorScheme.grabberAccent,
                  fontWeight: FontWeight.bold,
                  fontFamily: 'Oxanium',
                  letterSpacing: 1.2,
                ),
              ),
              backgroundColor: colorScheme.surfaceContainerHighest,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
                side: BorderSide(color: colorScheme.grabberAccent),
              ),
              duration: const Duration(seconds: 3),
            ),
          );
        }
      }
    } catch (e) {
      notifier.addLog('Export failed: $e', type: LogType.error);
    }
  }

  @override
  Widget build(BuildContext context) {
    final logs = ref.watch(logsProvider);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(l10n, theme, colorScheme),
          const SizedBox(height: 32),
          _buildSearchBox(l10n, colorScheme, theme),
          const SizedBox(height: 24),
          _buildTelemetrySection(logs, l10n, colorScheme),
          const SizedBox(height: 24),
          _buildResultsSection(l10n, colorScheme),
        ],
      ),
    );
  }

  Widget _buildHeader(
    AppLocalizations l10n,
    ThemeData theme,
    ColorScheme colorScheme,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "LINKS GRABBER",
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: colorScheme.grabberAccent,
            letterSpacing: 2,
            fontFamily: 'Oxanium',
            shadows: [Shadow(color: colorScheme.grabberAccent, blurRadius: 15)],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          "Find WhatsApp Group Links from the web using Google Dorking strategy.",
          style: TextStyle(
            color: colorScheme.onSurface.withValues(alpha: 0.5),
            fontSize: 12,
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }

  Widget _buildSearchBox(
    AppLocalizations l10n,
    ColorScheme colorScheme,
    ThemeData theme,
  ) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colorScheme.grabberCardBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: colorScheme.grabberAccent.withValues(alpha: 0.2),
        ),
        boxShadow: [
          BoxShadow(
            color: colorScheme.grabberAccent.withValues(alpha: 0.05),
            blurRadius: 10,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: _buildTextField(
              colorScheme: colorScheme,
              controller: _keywordController,
              label: "SEARCH KEYWORD",
              hint: "e.g. Crypto, Marketing, Real Estate",
              icon: Icons.radar_rounded,
            ),
          ),
          const SizedBox(width: 24),
          SizedBox(
            width: 150,
            child: _buildSlider(
              colorScheme: colorScheme,
              label: "SCAN LIMIT",
              value: _count.toDouble(),
              displayValue: "$_count Groups",
              min: 5,
              max: 100,
              onChanged: (v) => setState(() => _count = v.toInt()),
            ),
          ),
          const SizedBox(width: 24),
          SizedBox(
            height: 54,
            child: ElevatedButton.icon(
              onPressed: _isHunting ? null : _startHunt,
              icon: _isHunting
                  ? SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: colorScheme.onPrimaryContainer,
                      ),
                    )
                  : const Icon(Icons.travel_explore_rounded, size: 20),
              label: const Text(
                "START HUNT",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                  fontFamily: 'Oxanium',
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: colorScheme.grabberAccent.withValues(
                  alpha: 0.2,
                ),
                foregroundColor: colorScheme.grabberAccent,
                side: BorderSide(color: colorScheme.grabberAccent),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                padding: const EdgeInsets.symmetric(horizontal: 24),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTelemetrySection(
    List<LogEntry> logs,
    AppLocalizations l10n,
    ColorScheme colorScheme,
  ) {
    return _buildSection(
      colorScheme: colorScheme,
      title: "LIVE TELEMETRY",
      child: Container(
        height: 150,
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: colorScheme.surface.withValues(alpha: 0.5),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: colorScheme.grabberAccent.withValues(alpha: 0.2),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  "SYSTEM LOGS",
                  style: TextStyle(
                    color: colorScheme.grabberAccent,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                  ),
                ),
                if (_isHunting)
                  SizedBox(
                    width: 14,
                    height: 14,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: colorScheme.grabberAccent,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Divider(
              color: colorScheme.onSurface.withValues(alpha: 0.1),
              height: 1,
            ),
            const SizedBox(height: 8),
            Expanded(
              child: logs.isEmpty
                  ? Center(
                      child: Text(
                        "Waiting for commands...",
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: colorScheme.onSurface.withValues(alpha: 0.1),
                          fontSize: 10,
                          letterSpacing: 1.5,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    )
                  : ListView.builder(
                      itemCount: logs.length,
                      itemBuilder: (context, index) {
                        final log = logs[index];
                        if (!log.message.contains('Hunt') &&
                            log.type != LogType.error) {
                          return const SizedBox.shrink();
                        }

                        return Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Row(
                            children: [
                              Text(
                                '[${log.timestamp.toString().split(' ')[1].split('.')[0]}]',
                                style: TextStyle(
                                  color: colorScheme.onSurface.withValues(
                                    alpha: 0.3,
                                  ),
                                  fontSize: 10,
                                  fontFamily: 'monospace',
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  log.message,
                                  style: TextStyle(
                                    fontFamily: 'monospace',
                                    fontSize: 11,
                                    color: colorScheme.grabberAccent,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultsSection(AppLocalizations l10n, ColorScheme colorScheme) {
    if (_results.isEmpty && !_isHunting) {
      return Center(
        child: Column(
          children: [
            const SizedBox(height: 64),
            Icon(
              Icons.radar_rounded,
              size: 64,
              color: colorScheme.onSurface.withValues(alpha: 0.05),
            ),
            const SizedBox(height: 16),
            Text(
              "No groups found yet.",
              textAlign: TextAlign.center,
              style: TextStyle(
                color: colorScheme.onSurface.withValues(alpha: 0.1),
                letterSpacing: 1,
                fontFamily: 'Oxanium',
              ),
            ),
          ],
        ),
      );
    }

    return _buildSection(
      colorScheme: colorScheme,
      title: "RESULTS (${_results.length})",
      child: Column(
        children: [
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              childAspectRatio: 3,
            ),
            itemCount: _results.length,
            itemBuilder: (context, index) {
              final group = _results[index];
              final link = group['link'] as String;
              return Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  color: colorScheme.surfaceContainerHighest.withValues(
                    alpha: 0.3,
                  ),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: colorScheme.outline.withValues(alpha: 0.1),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.groups_rounded,
                      color: colorScheme.grabberAccent,
                      size: 24,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Group ${index + 1}',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            link,
                            style: TextStyle(
                              fontSize: 10,
                              color: colorScheme.onSurface.withValues(
                                alpha: 0.4,
                              ),
                              fontFamily: 'monospace',
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: Icon(
                        Icons.open_in_new_rounded,
                        size: 16,
                        color: colorScheme.onSurface.withValues(alpha: 0.3),
                      ),
                      onPressed: () async {
                        final uri = Uri.tryParse(link);
                        if (uri != null && await canLaunchUrl(uri)) {
                          await launchUrl(
                            uri,
                            mode: LaunchMode.externalApplication,
                          );
                        }
                      },
                    ),
                  ],
                ),
              );
            },
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            height: 50,
            child: OutlinedButton.icon(
              onPressed: _results.isEmpty ? null : _exportResults,
              icon: const Icon(Icons.table_view_rounded),
              label: const Text(
                "EXPORT TO EXCEL",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              style: OutlinedButton.styleFrom(
                foregroundColor: colorScheme.grabberAccent,
                side: BorderSide(color: colorScheme.grabberAccent),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField({
    required ColorScheme colorScheme,
    required TextEditingController controller,
    required String label,
    required String hint,
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
            color: colorScheme.onSurface.withValues(alpha: 0.5),
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
          inputFormatters: [
            FilteringTextInputFormatter.allow(
              RegExp(r'[a-zA-Z0-9\u0600-\u06FF\s,.\-_/]'),
            ),
          ],
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: TextStyle(
              color: colorScheme.onSurface.withValues(alpha: 0.2),
            ),
            prefixIcon: Icon(icon, size: 18, color: colorScheme.grabberAccent),
            filled: true,
            fillColor: colorScheme.surfaceContainerHighest.withValues(
              alpha: 0.3,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide.none,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSlider({
    required ColorScheme colorScheme,
    required String label,
    required double value,
    required String displayValue,
    required double min,
    required double max,
    required ValueChanged<double> onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
                color: colorScheme.onSurface.withValues(alpha: 0.5),
              ),
            ),
            Text(
              displayValue,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w900,
                color: colorScheme.grabberAccent,
                fontFamily: 'monospace',
              ),
            ),
          ],
        ),
        Slider(
          value: value,
          min: min,
          max: max,
          activeColor: colorScheme.grabberAccent,
          inactiveColor: colorScheme.outline.withValues(alpha: 0.2),
          onChanged: onChanged,
        ),
      ],
    );
  }

  Widget _buildSection({
    required ColorScheme colorScheme,
    required String title,
    required Widget child,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: colorScheme.grabberAccent,
            letterSpacing: 1.5,
          ),
        ),
        const SizedBox(height: 12),
        child,
      ],
    );
  }
}

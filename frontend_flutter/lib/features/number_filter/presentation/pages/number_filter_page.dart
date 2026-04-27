import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'package:g777_client/l10n/app_localizations_en.dart';
import 'dart:math';

typedef FilePickCallback = Future<String?> Function();

class NumberFilterPage extends ConsumerStatefulWidget {
  final FilePickCallback? pickFileCallback;

  const NumberFilterPage({super.key, this.pickFileCallback});

  @override
  ConsumerState<NumberFilterPage> createState() => _NumberFilterPageState();
}

class _NumberFilterPageState extends ConsumerState<NumberFilterPage>
    with SingleTickerProviderStateMixin {
  bool _isLoading = false;
  String? _filePath;
  Map<String, dynamic>? _summary;
  List<Map<String, dynamic>> _validNumbers = [];
  List<Map<String, dynamic>> _invalidNumbers = [];

  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _pickFile() async {
    final picker =
        widget.pickFileCallback ??
        () async {
          FilePickerResult? result = await FilePicker.pickFiles(
            type: FileType.custom,
            allowedExtensions: ['xlsx', 'csv'],
          );
          return result?.files.single.path;
        };

    final path = await picker();
    if (path != null) {
      setState(() => _filePath = path);
    }
  }

  Future<void> _startValidation() async {
    if (_filePath == null) return;
    setState(() {
      _isLoading = true;
      _summary = null;
      _validNumbers = [];
      _invalidNumbers = [];
    });

    try {
      await Future.delayed(const Duration(seconds: 2));

      // Mock processing logic
      final random = Random();
      const total = 100;
      const validCount = 85;
      const invalidCount = 15;

      List<Map<String, dynamic>> valid = [];
      List<Map<String, dynamic>> invalid = [];

      for (int i = 0; i < validCount; i++) {
        valid.add({
          'number': '+2010${random.nextInt(90000000) + 10000000}',
          'status': 'Registered',
        });
      }

      for (int i = 0; i < invalidCount; i++) {
        invalid.add({
          'number': '+2010${random.nextInt(90000000) + 10000000}',
          'status': 'Not Registered',
        });
      }

      setState(() {
        _validNumbers = valid;
        _invalidNumbers = invalid;
        _summary = {
          'total': total,
          'valid': validCount,
          'invalid': invalidCount,
        };
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  void _copyToClipboard(List<Map<String, dynamic>> data) {
    final text = data.map((e) => e['number']).join('\n');
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Copied to clipboard'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context) ?? AppLocalizationsEn();
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(l10n, colors),
          const SizedBox(height: 32),
          _buildActionCard(l10n, colors),
          if (_summary != null) ...[
            const SizedBox(height: 32),
            _buildResultsSection(l10n, colors, isDark),
          ],
        ],
      ),
    );
  }

  Widget _buildHeader(AppLocalizations l10n, ColorScheme colors) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        FittedBox(
          fit: BoxFit.scaleDown,
          child: Text(
            l10n.numberValidator.toUpperCase(),
            style: const TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
              fontFamily: 'Oxanium',
              color: Color(0xFF00F3FF),
            ),
          ),
        ),
        Text(
          l10n.numberValidatorDesc,
          style: TextStyle(
            color: colors.onSurface.withValues(alpha: 0.5),
            fontSize: 12,
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }

  Widget _buildActionCard(AppLocalizations l10n, ColorScheme colors) {
    final fileName = _filePath?.split('\\').last.split('/').last;

    return _buildSection(
      title: l10n.readyForScanning.toUpperCase(),
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: colors.surfaceContainer,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: colors.primary.withValues(alpha: 0.1)),
        ),
        child: Column(
          children: [
            const Icon(
              Icons.filter_alt_rounded,
              size: 48,
              color: Colors.white10,
            ),
            const SizedBox(height: 16),
            Text(
              "Select an Excel or CSV file containing the phone numbers you want to validate.",
              textAlign: TextAlign.center,
              style: TextStyle(
                color: colors.onSurface.withValues(alpha: 0.4),
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _pickFile,
                    icon: const Icon(Icons.file_upload_outlined),
                    label: FittedBox(
                      child: Text(
                        (fileName ?? "Choose Input File").toUpperCase(),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.2,
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Container(
                  height: 48,
                  width: 48,
                  decoration: BoxDecoration(
                    color: colors.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: IconButton(
                    onPressed: _isLoading || _filePath == null
                        ? null
                        : _startValidation,
                    icon: _isLoading
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.play_arrow_rounded),
                    color: colors.primary,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultsSection(
    AppLocalizations l10n,
    ColorScheme colors,
    bool isDark,
  ) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                "TOTAL",
                _summary!['total'].toString(),
                colors.primary,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                "VALID",
                _summary!['valid'].toString(),
                const Color(0xFF00FF41),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                "INVALID",
                _summary!['invalid'].toString(),
                Colors.redAccent,
              ),
            ),
          ],
        ),
        const SizedBox(height: 24),
        _buildSection(
          title: l10n.scanResults.toUpperCase(),
          child: Container(
            constraints: BoxConstraints(
              minHeight: 400,
              maxHeight: MediaQuery.of(context).size.height * 0.7,
            ),
            decoration: BoxDecoration(
              color: colors.surfaceContainer,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: colors.outline.withValues(alpha: 0.1)),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TabBar(
                  controller: _tabController,
                  indicatorColor: colors.primary,
                  labelColor: colors.primary,
                  unselectedLabelColor: colors.onSurface.withValues(alpha: 0.5),
                  tabs: [
                    Tab(
                      icon: const Icon(Icons.check_circle_outline),
                      text: '${l10n.validAccounts} (${_validNumbers.length})',
                    ),
                    Tab(
                      icon: const Icon(Icons.error_outline),
                      text:
                          '${l10n.corruptMissing} (${_invalidNumbers.length})',
                    ),
                  ],
                ),
                Expanded(
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildNumberList(
                        _validNumbers,
                        const Color(0xFF00FF41),
                        Icons.chat,
                        l10n,
                        true,
                      ),
                      _buildNumberList(
                        _invalidNumbers,
                        Colors.redAccent,
                        Icons.block,
                        l10n,
                        false,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildNumberList(
    List<Map<String, dynamic>> numbers,
    Color color,
    IconData icon,
    AppLocalizations l10n,
    bool isValid,
  ) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(12.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton.icon(
                onPressed: () => _copyToClipboard(numbers),
                icon: const Icon(Icons.copy, size: 16),
                label: const Text('Copy List'),
                style: TextButton.styleFrom(
                  foregroundColor: color,
                  backgroundColor: color.withValues(alpha: 0.1),
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView.separated(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            itemCount: numbers.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final item = numbers[index];
              return ListTile(
                dense: true,
                leading: Icon(icon, color: color, size: 20),
                title: Text(
                  item['number'],
                  style: const TextStyle(
                    fontFamily: 'monospace',
                    fontWeight: FontWeight.bold,
                  ),
                ),
                trailing: Text(
                  isValid ? 'WhatsApp Found' : 'Not Registered',
                  style: TextStyle(
                    fontSize: 10,
                    color: color.withValues(alpha: 0.8),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.1)),
      ),
      child: Column(
        children: [
          FittedBox(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 9,
                color: color.withValues(alpha: 0.7),
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 12),
          FittedBox(
            child: Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontFamily: 'monospace',
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSection({required String title, required Widget child}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.5,
          ),
        ),
        const SizedBox(height: 12),
        child,
      ],
    );
  }
}

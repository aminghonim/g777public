import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/api_service.dart';
import 'package:g777_client/shared/providers/logs_provider.dart';
import 'package:g777_client/l10n/app_localizations.dart';

class AccountWarmerPage extends ConsumerStatefulWidget {
  const AccountWarmerPage({super.key});

  @override
  ConsumerState<AccountWarmerPage> createState() => _AccountWarmerPageState();
}

class _AccountWarmerPageState extends ConsumerState<AccountWarmerPage> {
  final ApiService _api = ApiService();
  final _phone1Controller = TextEditingController();
  final _phone2Controller = TextEditingController();
  int _count = 50;
  int _delay = 60;
  bool _isRunning = false;

  @override
  void dispose() {
    _phone1Controller.dispose();
    _phone2Controller.dispose();
    super.dispose();
  }

  Future<void> _toggleWarming() async {
    final notifier = ref.read(logsProvider.notifier);
    setState(() => _isRunning = !_isRunning);

    if (_isRunning) {
      try {
        await _api.startWarming(
          phone1: _phone1Controller.text,
          phone2: _phone2Controller.text,
          count: _count,
          delay: _delay,
        );
        notifier.addLog(
          'Warming sequence initiated between accounts.',
          type: LogType.success,
        );
      } catch (e) {
        setState(() => _isRunning = false);
        notifier.addLog('Error starting warmer: $e', type: LogType.error);
      }
    } else {
      try {
        await _api.stopWarming();
        notifier.addLog('Warming sequence terminated.', type: LogType.warning);
      } catch (e) {
        notifier.addLog('Error stopping warmer: $e', type: LogType.error);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final logs = ref.watch(logsProvider);
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final l10n = AppLocalizations.of(context)!;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(l10n, theme),
          const SizedBox(height: 32),
          _buildConfigCard(l10n, theme, isDark),
          const SizedBox(height: 24),
          _buildLogConsole(logs, l10n, theme, isDark),
        ],
      ),
    );
  }

  Widget _buildHeader(AppLocalizations l10n, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.accountWarmer.toUpperCase(),
          style: const TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Color(0xFF00F3FF),
            letterSpacing: 2,
            fontFamily: 'Oxanium',
            shadows: [Shadow(color: Color(0xFF00F3FF), blurRadius: 15)],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          l10n.accountWarmerDesc,
          style: TextStyle(
            color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
            fontSize: 12,
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }

  Widget _buildConfigCard(AppLocalizations l10n, ThemeData theme, bool isDark) {
    final colorScheme = theme.colorScheme;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: isDark
            ? const Color(0xFF0F0F23).withValues(alpha: 0.8)
            : theme.cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isDark
              ? const Color(0xFF00F3FF).withValues(alpha: 0.3)
              : colorScheme.primary.withValues(alpha: 0.1),
        ),
        boxShadow: isDark
            ? [
                BoxShadow(
                  color: const Color(0xFF00F3FF).withValues(alpha: 0.05),
                  blurRadius: 10,
                  spreadRadius: 2,
                ),
              ]
            : null,
      ),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: _buildTextField(
                  label: l10n.phoneJid1,
                  controller: _phone1Controller,
                  hint: '201012345678@s.whatsapp.net',
                  icon: Icons.account_circle_outlined,
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Icon(
                  Icons.swap_horiz_rounded,
                  color: const Color(0xFF00FF41),
                  shadows: [
                    Shadow(
                      color: const Color(0xFF00FF41).withValues(alpha: 0.5),
                      blurRadius: 10,
                    ),
                  ],
                ),
              ),
              Expanded(
                child: _buildTextField(
                  label: l10n.phoneJid2,
                  controller: _phone2Controller,
                  hint: '201098765432@s.whatsapp.net',
                  icon: Icons.account_circle_outlined,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: _buildSlider(
                  label: l10n.totalMessages.toUpperCase(),
                  value: _count.toDouble(),
                  displayValue: '$_count MSGS',
                  min: 10,
                  max: 500,
                  onChanged: (v) => setState(() => _count = v.toInt()),
                ),
              ),
              const SizedBox(width: 32),
              Expanded(
                child: _buildSlider(
                  label: l10n.averageDelay.toUpperCase(),
                  value: _delay.toDouble(),
                  displayValue: '${_delay}S',
                  min: 5,
                  max: 300,
                  onChanged: (v) => setState(() => _delay = v.toInt()),
                ),
              ),
            ],
          ),
          const SizedBox(height: 32),
          SizedBox(
            width: double.infinity,
            height: 54,
            child: ElevatedButton.icon(
              onPressed: _toggleWarming,
              icon: Icon(
                _isRunning ? Icons.stop_rounded : Icons.play_arrow_rounded,
                size: 20,
              ),
              label: Text(
                _isRunning
                    ? l10n.terminateWarming.toUpperCase()
                    : l10n.startWarming.toUpperCase(),
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                  fontFamily: 'Oxanium',
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _isRunning
                    ? Colors.redAccent.withValues(alpha: 0.2)
                    : const Color(0xFF00FF41).withValues(alpha: 0.2),
                foregroundColor: _isRunning
                    ? Colors.redAccent
                    : const Color(0xFF00FF41),
                side: BorderSide(
                  color: _isRunning
                      ? Colors.redAccent
                      : const Color(0xFF00FF41),
                ),
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
    required TextEditingController controller,
    required String hint,
    required IconData icon,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.5,
            color: Colors.white38,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: const TextStyle(color: Colors.white12),
            prefixIcon: Icon(icon, size: 18, color: const Color(0xFF00F3FF)),
            filled: true,
            fillColor: Colors.black26,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 12,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: Colors.white.withValues(alpha: 0.05),
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: Colors.white.withValues(alpha: 0.05),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSlider({
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
              style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
                color: Colors.white38,
              ),
            ),
            Text(
              displayValue,
              style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w900,
                color: Color(0xFF00F3FF),
                fontFamily: 'monospace',
              ),
            ),
          ],
        ),
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            trackHeight: 2,
            thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
            overlayShape: const RoundSliderOverlayShape(overlayRadius: 14),
          ),
          child: Slider(
            value: value,
            min: min,
            max: max,
            activeColor: const Color(0xFF00F3FF),
            inactiveColor: Colors.white10,
            onChanged: onChanged,
          ),
        ),
      ],
    );
  }

  Widget _buildLogConsole(
    List<LogEntry> logs,
    AppLocalizations l10n,
    ThemeData theme,
    bool isDark,
  ) {
    return Container(
      height: 300,
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF00F3FF).withValues(alpha: 0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l10n.warmingTelemetry.toUpperCase(),
                style: const TextStyle(
                  color: Color(0xFF00F3FF),
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                ),
              ),
              if (_isRunning)
                const Icon(
                  Icons.sensors_rounded,
                  size: 14,
                  color: Color(0xFF00FF41),
                ),
            ],
          ),
          const SizedBox(height: 8),
          const Divider(color: Colors.white12, height: 1),
          const SizedBox(height: 8),
          Expanded(
            child: logs.isEmpty
                ? Center(
                    child: Text(
                      l10n.noActivity.toUpperCase(),
                      style: const TextStyle(
                        color: Colors.white10,
                        fontSize: 10,
                        letterSpacing: 2,
                      ),
                    ),
                  )
                : ListView.builder(
                    itemCount: logs.length,
                    itemBuilder: (context, index) {
                      final log = logs[index];
                      Color logColor = const Color(0xFF00FF41);
                      if (log.type == LogType.error) {
                        logColor = Colors.redAccent;
                      }
                      if (log.type == LogType.warning) {
                        logColor = Colors.orangeAccent;
                      }
                      if (log.type == LogType.success) {
                        logColor = const Color(0xFF00F3FF);
                      }

                      return Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '[${log.timestamp.toString().split(' ')[1].split('.')[0]}]',
                              style: const TextStyle(
                                color: Colors.white24,
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
                                  fontSize: 12,
                                  color: logColor,
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
    );
  }
}

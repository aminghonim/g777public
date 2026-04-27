import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/api_service.dart';
import 'package:g777_client/shared/providers/logs_provider.dart';
import 'package:g777_client/l10n/app_localizations.dart';

class PollSenderPage extends ConsumerStatefulWidget {
  const PollSenderPage({super.key});

  @override
  ConsumerState<PollSenderPage> createState() => _PollSenderPageState();
}

class _PollSenderPageState extends ConsumerState<PollSenderPage> {
  final ApiService _api = ApiService();
  final _jidController = TextEditingController();
  final _questionController = TextEditingController();
  final List<TextEditingController> _optionControllers = [
    TextEditingController(),
    TextEditingController(),
  ];
  bool _isSending = false;

  @override
  void dispose() {
    _jidController.dispose();
    _questionController.dispose();
    for (var c in _optionControllers) {
      c.dispose();
    }
    super.dispose();
  }

  void _addOption() {
    setState(() {
      _optionControllers.add(TextEditingController());
    });
  }

  void _removeOption(int index) {
    if (_optionControllers.length > 2) {
      setState(() {
        _optionControllers[index].dispose();
        _optionControllers.removeAt(index);
      });
    }
  }

  Future<void> _sendPoll() async {
    final notifier = ref.read(logsProvider.notifier);
    setState(() => _isSending = true);

    try {
      final options = _optionControllers
          .map((c) => c.text)
          .where((t) => t.isNotEmpty)
          .toList();

      if (_jidController.text.isEmpty) {
        throw Exception('Target Group JID is required');
      }

      await _api.sendPoll(
        jid: _jidController.text,
        question: _questionController.text,
        options: options,
      );
      notifier.addLog(
        "Poll initiated: ${_questionController.text}",
        type: LogType.success,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Poll Campaign Launched Successfully!"),
            backgroundColor: Color(0xFFFF00D9),
          ),
        );
      }
    } catch (e) {
      notifier.addLog('Error: $e', type: LogType.error);
    } finally {
      setState(() => _isSending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final logs = ref.watch(logsProvider);
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(theme, l10n),
          const SizedBox(height: 32),
          _buildPollEditor(theme, isDark, l10n),
          const SizedBox(height: 24),
          _buildLogConsole(logs, theme, isDark, l10n),
        ],
      ),
    );
  }

  Widget _buildHeader(ThemeData theme, AppLocalizations l10n) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "POLL SENDER",
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: Color(0xFFFF00D9), // Neon Pink
            letterSpacing: 2,
            fontFamily: 'Oxanium',
            shadows: [Shadow(color: Color(0xFFFF00D9), blurRadius: 15)],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Send interactive polls to your contact lists to increase engagement.', // Keep or localize
          style: TextStyle(
            color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
            fontSize: 12,
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }

  Widget _buildPollEditor(ThemeData theme, bool isDark, AppLocalizations l10n) {
    final colorScheme = theme.colorScheme;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: isDark
            ? const Color(0xFF160A16).withValues(alpha: 0.8)
            : theme.cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isDark
              ? const Color(0xFFFF00D9).withValues(alpha: 0.3)
              : colorScheme.primary.withValues(alpha: 0.1),
        ),
        boxShadow: isDark
            ? [
                BoxShadow(
                  color: const Color(0xFFFF00D9).withValues(alpha: 0.05),
                  blurRadius: 10,
                  spreadRadius: 2,
                ),
              ]
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'TARGET GROUP JID',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.5,
              color: Colors.white38,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _jidController,
            style: const TextStyle(fontFamily: 'monospace', fontSize: 13),
            decoration: InputDecoration(
              hintText: 'e.g. 123456789@g.us',
              hintStyle: const TextStyle(color: Colors.white12),
              filled: true,
              fillColor: Colors.black26,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(
                  color: Colors.white.withValues(alpha: 0.05),
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            "POLL QUESTION",
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.5,
              color: Colors.white38,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _questionController,
            style: const TextStyle(fontFamily: 'Oxanium', fontSize: 14),
            decoration: InputDecoration(
              hintText: "Ask something engaging...",
              hintStyle: const TextStyle(color: Colors.white12),
              filled: true,
              fillColor: Colors.black26,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(
                  color: Colors.white.withValues(alpha: 0.05),
                ),
              ),
            ),
          ),
          const SizedBox(height: 32),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "POLL OPTIONS",
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                  color: Colors.white38,
                ),
              ),
              TextButton.icon(
                onPressed: _addOption,
                icon: const Icon(Icons.add_circle_outline, size: 16),
                label: const Text(
                  "ADD OPTION",
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                style: TextButton.styleFrom(
                  foregroundColor: const Color(0xFFFF00D9),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...List.generate(_optionControllers.length, (i) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _optionControllers[i],
                      style: const TextStyle(fontSize: 13),
                      decoration: InputDecoration(
                        hintText: "Option ${i + 1}",
                        hintStyle: const TextStyle(color: Colors.white12),
                        prefixIcon: const Icon(
                          Icons.radio_button_unchecked,
                          size: 16,
                          color: Color(0xFFFF00D9),
                        ),
                        filled: true,
                        fillColor: Colors.black26,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: BorderSide(
                            color: Colors.white.withValues(alpha: 0.05),
                          ),
                        ),
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(
                      Icons.delete_outline,
                      color: Colors.redAccent,
                      size: 18,
                    ),
                    onPressed: () => _removeOption(i),
                  ),
                ],
              ),
            );
          }),
          const SizedBox(height: 32),
          SizedBox(
            width: double.infinity,
            height: 54,
            child: ElevatedButton.icon(
              onPressed: _isSending ? null : _sendPoll,
              icon: _isSending
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.black,
                      ),
                    )
                  : const Icon(Icons.send_rounded, size: 20),
              label: const Text(
                "LAUNCH CAMPAIGN",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                  fontFamily: 'Oxanium',
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFFF00D9).withValues(alpha: 0.2),
                foregroundColor: const Color(0xFFFF00D9),
                side: const BorderSide(color: Color(0xFFFF00D9)),
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

  Widget _buildLogConsole(
    List<LogEntry> logs,
    ThemeData theme,
    bool isDark,
    AppLocalizations l10n,
  ) {
    return Container(
      height: 250,
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFFFF00D9).withValues(alpha: 0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "CAMPAIGN TELEMETRY",
            style: TextStyle(
              color: Color(0xFFFF00D9),
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 8),
          const Divider(color: Colors.white12, height: 1),
          const SizedBox(height: 8),
          Expanded(
            child:
                logs
                    .where(
                      (l) =>
                          l.message.contains('Poll') || l.type == LogType.error,
                    )
                    .isEmpty
                ? const Center(
                    child: Text(
                      "READY FOR COMMANDS",
                      style: TextStyle(
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
                      Color logColor = const Color(0xFFFF00D9);
                      if (log.type == LogType.error) {
                        logColor = Colors.redAccent;
                      }
                      if (log.type == LogType.success) {
                        logColor = Colors.greenAccent;
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

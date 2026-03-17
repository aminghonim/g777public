import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'package:g777_client/shared/painters/custom_painters.dart';
import 'package:g777_client/shared/providers/logs_provider.dart';
import 'package:go_router/go_router.dart';
import '../controllers/group_sender_controller.dart';
import 'package:g777_client/core/theme/theme.dart'; // Unified theme system

class GroupSenderPage extends ConsumerStatefulWidget {
  const GroupSenderPage({super.key});

  @override
  ConsumerState<GroupSenderPage> createState() => _GroupSenderPageState();
}

class _GroupSenderPageState extends ConsumerState<GroupSenderPage> {
  final List<TextEditingController> _messageControllers = [
    TextEditingController(),
    TextEditingController(),
    TextEditingController(),
  ];

  final TextEditingController _groupLinkController = TextEditingController();

  double _minDelay = 5;
  double _maxDelay = 15;
  bool _paramsProcessed = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _processQueryParams());
  }

  void _processQueryParams() {
    if (_paramsProcessed) return;

    final state = GoRouterState.of(context);
    final phone = state.uri.queryParameters['phone'];
    final name = state.uri.queryParameters['name'];

    if (phone != null && phone.isNotEmpty) {
      final notifier = ref.read(groupSenderProvider.notifier);
      notifier.setDirectContact(phone: phone, name: name ?? 'Lead');

      // Pre-fill message
      if (name != null) {
        _messageControllers[0].text =
            "Hello $name, I found your business and I'm interested in your services. Can we talk?";
      } else {
        _messageControllers[0].text =
            "Hello, I found your contact and I'm interested in your services. Can we talk?";
      }
    }

    setState(() => _paramsProcessed = true);
  }

  @override
  void dispose() {
    for (var controller in _messageControllers) {
      controller.dispose();
    }
    _groupLinkController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;

    final state = ref.watch(groupSenderProvider);
    final notifier = ref.read(groupSenderProvider.notifier);

    ref.watch(campaignStreamListenerProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: SelectionArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildPageHeader(colorScheme, l10n),
              const SizedBox(height: 32),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    flex: 3,
                    child: Column(
                      children: [
                        _buildImportCard(
                          context,
                          colorScheme,
                          l10n,
                          state,
                          notifier,
                        ),
                        const SizedBox(height: 24),
                        _buildCampaignContentCard(context, colorScheme, l10n),
                      ],
                    ),
                  ),
                  const SizedBox(width: 24),
                  Expanded(
                    flex: 2,
                    child: Column(
                      children: [
                        _buildEngineSettingsCard(context, colorScheme, l10n),
                        const SizedBox(height: 24),
                        _buildTelemetryConsole(context, colorScheme, l10n),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 40),
              _buildLaunchButton(context, colorScheme, l10n, state, notifier),
            ],
          ), // closes Column
        ), // closes SingleChildScrollView
      ), // closes SelectionArea
    );
  }

  Widget _buildPageHeader(ColorScheme colorScheme, AppLocalizations l10n) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.groupSender.toUpperCase(),
          style: TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.bold,
            letterSpacing: 2,
            fontFamily: 'Oxanium',
            color: colorScheme.onSurface,
          ),
        ),
        Text(
          "ADVANCED BROADCAST ENGINE V2.2",
          style: TextStyle(
            fontSize: 12,
            color: colorScheme.onSurface.withValues(alpha: 0.4),
            letterSpacing: 4,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildImportCard(
    BuildContext context,
    ColorScheme colorScheme,
    AppLocalizations l10n,
    GroupSenderState state,
    GroupSenderNotifier notifier,
  ) {
    String label = state.uploadedFileName ?? l10n.chooseDataSource;
    bool hasSource = state.uploadedFileName != null;
    Color statusColor = colorScheme.groupSenderAccent;

    if (state.directContacts != null) {
      label = "Direct Target: (Source: Link)";
      hasSource = true;
      statusColor = colorScheme.statusWarning;
    }

    return _BaseCard(
      title: l10n.excelDataFeed,
      child: Column(
        children: [
          _ActionButton(
            label: label,
            icon: state.directContacts != null
                ? Icons.person_pin_circle
                : Icons.upload_file_rounded,
            color: statusColor,
            isLoading: state.isLoading,
            onPressed: notifier.pickAndUploadExcel,
          ),
          if (hasSource)
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Text(
                state.directContacts != null
                    ? "SYSTEM READY: ENGAGEMENT MODE"
                    : l10n.readyFile(state.uploadedFileName!),
                style: TextStyle(
                  color: state.directContacts != null
                      ? colorScheme.statusWarning
                      : colorScheme.statusOnline,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildCampaignContentCard(
    BuildContext context,
    ColorScheme colorScheme,
    AppLocalizations l10n,
  ) {
    return _BaseCard(
      title: l10n.campaignContent,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextField(
            controller: _groupLinkController,
            decoration: _inputDecoration(
              colorScheme,
              l10n.groupLinkOptional,
              Icons.link,
            ),
          ),
          const SizedBox(height: 20),
          ...List.generate(_messageControllers.length, (index) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: TextField(
                controller: _messageControllers[index],
                maxLines: 4,
                decoration: _inputDecoration(
                  colorScheme,
                  l10n.msgVariant(index + 1),
                  Icons.message_rounded,
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildEngineSettingsCard(
    BuildContext context,
    ColorScheme colorScheme,
    AppLocalizations l10n,
  ) {
    return _BaseCard(
      title: l10n.engineSettings,
      child: Column(
        children: [
          _buildDelaySlider(colorScheme, l10n.minDelay, _minDelay, 1, 60, (v) {
            setState(() => _minDelay = v);
          }),
          const SizedBox(height: 16),
          _buildDelaySlider(colorScheme, l10n.maxDelay, _maxDelay, 5, 120, (v) {
            setState(() => _maxDelay = v);
          }),
        ],
      ),
    );
  }

  Widget _buildDelaySlider(
    ColorScheme colorScheme,
    String label,
    double value,
    double min,
    double max,
    ValueChanged<double> onChanged,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: colorScheme.onSurface.withValues(alpha: 0.5),
              ),
            ),
            Text(
              "${value.toInt()}s",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: colorScheme.sendProgress,
              ),
            ),
          ],
        ),
        Slider(
          value: value,
          min: min,
          max: max,
          onChanged: onChanged,
          activeColor: colorScheme.sendProgress,
        ),
      ],
    );
  }

  Widget _buildTelemetryConsole(
    BuildContext context,
    ColorScheme colorScheme,
    AppLocalizations l10n,
  ) {
    final logs = ref.watch(logsProvider);
    return _BaseCard(
      title: l10n.logs,
      child: Container(
        height: 300,
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
          borderRadius: BorderRadius.circular(12),
        ),
        child: logs.isEmpty
            ? Center(
                child: Text(
                  l10n.noActivity,
                  style: TextStyle(
                    color: colorScheme.onSurface.withValues(alpha: 0.4),
                  ),
                ),
              )
            : ListView.builder(
                padding: const EdgeInsets.all(12),
                itemCount: logs.length,
                itemBuilder: (context, index) {
                  final log = logs[index];
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: Text(
                      "[${log.timestamp.hour}:${log.timestamp.minute}] ${log.message}",
                      style: TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 11,
                        color: log.type == LogType.error
                            ? colorScheme.error
                            : log.type == LogType.success
                            ? colorScheme.statusOnline
                            : colorScheme.onSurface.withValues(alpha: 0.7),
                      ),
                    ),
                  );
                },
              ),
      ),
    );
  }

  Widget _buildLaunchButton(
    BuildContext context,
    ColorScheme colorScheme,
    AppLocalizations l10n,
    GroupSenderState state,
    GroupSenderNotifier notifier,
  ) {
    return Center(
      child: SizedBox(
        width: 300,
        height: 80,
        child: ElevatedButton(
          onPressed: state.isCampaignRunning
              ? null
              : () => notifier.launchCampaign(
                  messages: _messageControllers
                      .map((c) => c.text)
                      .where((t) => t.isNotEmpty)
                      .toList(),
                  groupLink: _groupLinkController.text,
                  delayMin: _minDelay.toInt(),
                  delayMax: _maxDelay.toInt(),
                ),
          style: ElevatedButton.styleFrom(
            backgroundColor: colorScheme.groupSenderAccent.withValues(
              alpha: 0.1,
            ),
            foregroundColor: colorScheme.groupSenderAccent,
            padding: EdgeInsets.zero,
            shape: AppBeveledRectangleBorder(
              side: BorderSide(color: colorScheme.groupSenderAccent, width: 2),
              bevelSize: 20,
            ),
          ),
          child: Stack(
            alignment: Alignment.center,
            children: [
              if (state.isCampaignRunning)
                Positioned.fill(
                  child: LinearProgressIndicator(
                    value: state.progress,
                    backgroundColor: Colors.transparent,
                    valueColor: AlwaysStoppedAnimation(
                      colorScheme.groupSenderAccent.withValues(alpha: 0.2),
                    ),
                  ),
                ),
              Text(
                state.isCampaignRunning
                    ? l10n.executingCampaign.toUpperCase()
                    : l10n.launchCampaign.toUpperCase(),
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 2,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  InputDecoration _inputDecoration(
    ColorScheme colorScheme,
    String label,
    IconData icon,
  ) {
    return InputDecoration(
      labelText: label,
      prefixIcon: Icon(
        icon,
        size: 20,
        color: colorScheme.primary.withValues(alpha: 0.7),
      ),
      labelStyle: TextStyle(
        fontSize: 12,
        color: colorScheme.onSurface.withValues(alpha: 0.6),
      ),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: colorScheme.outline.withValues(alpha: 0.2),
        ),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: colorScheme.primary, width: 2),
      ),
    );
  }
}

class _BaseCard extends StatelessWidget {
  final String title;
  final Widget child;

  const _BaseCard({required this.title, required this.child});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: colorScheme.outline.withValues(alpha: 0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title.toUpperCase(),
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.5,
              color: colorScheme.onSurface.withValues(alpha: 0.5),
            ),
          ),
          const SizedBox(height: 20),
          child,
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  final bool isLoading;
  final VoidCallback onPressed;

  const _ActionButton({
    required this.label,
    required this.icon,
    required this.color,
    required this.isLoading,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 60,
      child: OutlinedButton.icon(
        onPressed: isLoading ? null : onPressed,
        icon: isLoading
            ? SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2, color: color),
              )
            : Icon(icon, color: color),
        label: Text(
          label.toUpperCase(),
          style: TextStyle(color: color, fontWeight: FontWeight.bold),
        ),
        style: OutlinedButton.styleFrom(
          side: BorderSide(color: color.withValues(alpha: 0.5)),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }
}

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:g777_client/core/services/api_service.dart';
import 'package:g777_client/l10n/app_localizations.dart';

class PairingDialog extends StatefulWidget {
  const PairingDialog({super.key});

  @override
  State<PairingDialog> createState() => _PairingDialogState();
}

class _PairingDialogState extends State<PairingDialog> {
  final ApiService _api = ApiService();
  final TextEditingController _phoneController = TextEditingController();

  String? _qrBase64;
  String? _pairingCode;
  bool _isLoading = false;
  String? _error;
  bool _isUsingPhone = false;
  String? _status;

  @override
  void initState() {
    super.initState();
    _fetchQR();
  }

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _fetchQR() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _error = null;
      _pairingCode = null;
    });
    try {
      final res = await _api.getQRCode();
      if (!mounted) return;
      if (res['success'] == true) {
        final data = res['data'];
        setState(() {
          _qrBase64 = data['base64'];
          _status = data['status'];
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = res['error'];
          _isLoading = false;
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _fetchPairingCode() async {
    if (_phoneController.text.isEmpty) return;
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _error = null;
      _qrBase64 = null;
    });
    try {
      final res = await _api.getPairingCode(_phoneController.text);
      if (!mounted) return;
      if (res['success'] == true) {
        setState(() {
          _pairingCode = res['code'];
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = res['message'];
          _isLoading = false;
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _handleLogout() async {
    if (!mounted) return;
    setState(() => _isLoading = true);
    try {
      await _api.logout();
      if (!mounted) return;
      // After logout, wait a bit for bridge to restart and then fetch QR
      await Future.delayed(const Duration(seconds: 3));
      _fetchQR();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = "Logout failed: $e";
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final accent = isDark ? const Color(0xFF00F3FF) : theme.colorScheme.primary;
    final l10n = AppLocalizations.of(context)!;

    return Dialog(
      backgroundColor: isDark
          ? const Color(0xFF0F0F23)
          : theme.colorScheme.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(24),
        side: BorderSide(color: accent, width: 1),
      ),
      child: Container(
        width: 400,
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              l10n.pairingDialogTitle.toUpperCase(),
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: accent,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 24),

            // Toggle
            Row(
              children: [
                Expanded(
                  child: _buildTypeButton(
                    l10n.qrCode.toUpperCase(),
                    !_isUsingPhone,
                    () {
                      setState(() => _isUsingPhone = false);
                      _fetchQR();
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildTypeButton(
                    l10n.phoneNumber.toUpperCase(),
                    _isUsingPhone,
                    () {
                      setState(() => _isUsingPhone = true);
                    },
                  ),
                ),
              ],
            ),

            const SizedBox(height: 32),

            if (_isUsingPhone && _pairingCode == null) ...[
              TextField(
                controller: _phoneController,
                style: TextStyle(
                  color: isDark ? Colors.white : theme.colorScheme.onSurface,
                  fontFamily: 'monospace',
                ),
                decoration: InputDecoration(
                  labelText: l10n.phoneLabel.toUpperCase(),
                  labelStyle: TextStyle(
                    color: isDark
                        ? Colors.white38
                        : theme.colorScheme.onSurface.withValues(alpha: 0.5),
                    fontSize: 10,
                  ),
                  hintText: l10n.phoneHint,
                  hintStyle: TextStyle(
                    color: isDark
                        ? Colors.white10
                        : theme.colorScheme.onSurface.withValues(alpha: 0.2),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(
                      color: isDark
                          ? Colors.white.withValues(alpha: 0.1)
                          : theme.colorScheme.outline,
                    ),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: accent),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _fetchPairingCode,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: accent,
                    foregroundColor: Colors.black,
                  ),
                  child: Text(l10n.generateCode.toUpperCase()),
                ),
              ),
            ],

            if (_isLoading)
              SizedBox(
                height: 200,
                child: Center(child: CircularProgressIndicator(color: accent)),
              )
            else ...[
              if (_error != null)
                Padding(
                  padding: const EdgeInsets.all(20),
                  child: SelectableText(
                    'ERROR: $_error',
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.redAccent, fontSize: 12),
                  ),
                ),
              if (_qrBase64 != null && !_isUsingPhone)
                Column(
                  children: [
                    if (_status == 'ALREADY_CONNECTED')
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 40),
                        child: Column(
                          children: [
                            Icon(Icons.check_circle_outline, color: accent, size: 48),
                            const SizedBox(height: 16),
                            Text(
                              "WHATSAPP ALREADY CONNECTED",
                              style: TextStyle(color: accent, fontWeight: FontWeight.bold, fontSize: 12),
                            ),
                          ],
                        ),
                      )
                    else
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Image.memory(
                          base64Decode(_qrBase64!.split(',').last),
                          width: 220,
                          height: 220,
                        ),
                      ),
                  ],
                )
              else if (_pairingCode != null && _isUsingPhone)
                Container(
                  padding: const EdgeInsets.symmetric(
                    vertical: 32,
                    horizontal: 24,
                  ),
                  decoration: BoxDecoration(
                    color: accent.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: accent.withValues(alpha: 0.3)),
                  ),
                  child: SelectableText(
                    _pairingCode!,
                    style: TextStyle(
                      fontSize: 42,
                      fontWeight: FontWeight.w900,
                      color: accent,
                      letterSpacing: 8,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),

              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  TextButton.icon(
                    onPressed: _isLoading ? null : _fetchQR,
                    icon: const Icon(Icons.refresh, size: 16),
                    label: const Text("REFRESH", style: TextStyle(fontSize: 10)),
                    style: TextButton.styleFrom(foregroundColor: accent),
                  ),
                  const SizedBox(width: 8),
                  TextButton.icon(
                    onPressed: _isLoading ? null : _handleLogout,
                    icon: const Icon(Icons.power_settings_new, size: 16),
                    label: const Text("FORCED RESET", style: TextStyle(fontSize: 10)),
                    style: TextButton.styleFrom(foregroundColor: Colors.redAccent),
                  ),
                ],
              ),
            ],

            const SizedBox(height: 16),
            SelectableText(
              _isUsingPhone
                  ? l10n.pairingCodeInstructions.toUpperCase()
                  : l10n.qrInstructions.toUpperCase(),
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 10,
                color: Colors.white54,
                letterSpacing: 1,
              ),
            ),
            const SizedBox(height: 24),
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(
                l10n.close.toUpperCase(),
                style: TextStyle(color: accent),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTypeButton(String label, bool isSelected, VoidCallback onTap) {
    const accent = Color(0xFF00F3FF);
    return InkWell(
      onTap: onTap,
      child: Container(
        height: 48,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: isSelected
              ? accent.withValues(alpha: 0.1)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? accent : Colors.white.withValues(alpha: 0.1),
          ),
        ),
        child: SelectableText(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.bold,
            color: isSelected ? accent : Colors.white54,
            letterSpacing: 1,
          ),
        ),
      ),
    );
  }
}

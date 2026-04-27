import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_theme.dart';
import '../../../../shared/painters/custom_painters.dart';
import '../../../../core/utils/hwid_generator.dart';
import '../../../../core/services/api_client.dart';
import '../../../../core/security/secure_storage_service.dart';
import '../../providers/auth_provider.dart';

/// SAAS-016: License Activation Screen
/// Premium desktop-oriented hardware binding page.
class LicenseActivationPage extends ConsumerStatefulWidget {
  const LicenseActivationPage({super.key});

  @override
  ConsumerState<LicenseActivationPage> createState() =>
      _LicenseActivationPageState();
}

class _LicenseActivationPageState extends ConsumerState<LicenseActivationPage>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _licenseController = TextEditingController();

  bool _isLoading = false;
  String? _errorMessage;

  late AnimationController _animController;
  late Animation<double> _fadeAnim;
  late Animation<Offset> _slideAnim;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _fadeAnim = CurvedAnimation(parent: _animController, curve: Curves.easeOut);
    _slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.08),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _animController, curve: Curves.easeOut));
    _animController.forward();
  }

  @override
  void dispose() {
    _animController.dispose();
    _licenseController.dispose();
    super.dispose();
  }

  /// DEV BYPASS: If the key is a single digit 1-9, activate locally without API.
  bool _isDevKey(String key) {
    return RegExp(r'^[1-9]$').hasMatch(key);
  }

  Future<void> _handleActivation() async {
    if (!_formKey.currentState!.validate()) return;

    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final licenseKey = _licenseController.text.trim().toUpperCase();

      // DEV MODE: Accept digits 1-9 as instant local activation keys.
      if (_isDevKey(_licenseController.text.trim())) {
        final devToken = 'dev-token-local-$licenseKey';
        final syntheticUser = {
          'id': 'dev-id-$licenseKey',
          'username': 'developer_$licenseKey',
          'role': 'client',
          'instance_name': 'DevInst_$licenseKey',
        };

        await SecureStorageService.write('jwt_token', devToken);
        await SecureStorageService.write(
          'user_data',
          jsonEncode(syntheticUser),
        );

        ref.invalidate(authProvider);

        if (mounted) {
          context.go('/dashboard');
        }
        return;
      }

      // 1. Silent Extract HWID (ASVS V11.5.1 Compliant)
      final hwid = await HwidGenerator.generate();

      final apiClient = ref.read(apiClientProvider);

      // 2. Validate Key and Bind Device
      final response = await apiClient.post(
        '/auth/license/activate',
        body: {'license_key': licenseKey, 'hwid': hwid},
      );

      // 3. Store Synthetic User Logic locally
      if (response.isSuccess) {
        final token = response.data['access_token'] as String;
        // Mock User Structure to satisfy 100% Zero-Regression
        final syntheticUser = {
          'id': 'synthetic-id-$licenseKey',
          'username': licenseKey,
          'role': 'client',
          'instance_name': 'Inst_${licenseKey.substring(0, 8)}',
        };

        await SecureStorageService.write('jwt_token', token);
        await SecureStorageService.write(
          'user_data',
          jsonEncode(syntheticUser),
        );

        // 4. Force auth state refresh via invalidation
        ref.invalidate(authProvider);

        if (mounted) {
          context.go('/dashboard');
        }
      } else {
        setState(() {
          _errorMessage = "Failed to activate license.";
        });
      }
    } on ApiException catch (e) {
      setState(() {
        _errorMessage = e.message;
      });
    } catch (e) {
      setState(() {
        _errorMessage = "An unexpected error occurred.";
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Matching Premium Desktop Theme Design
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final colors = AppTheme.getThemeColors(isDark);

    return SelectionArea(
      child: Scaffold(
        backgroundColor: colors.backgroundPrimary,
        body: Stack(
          children: [
            // Cyberpunk/Circuit Matrix BG
            CustomPaint(
              painter: CircuitBackgroundPainter(isDark: isDark),
              size: Size.infinite,
            ),

            // Optional Back Button (If trial not expired)
            _buildBackButton(context, ref, colors),

            Center(
              child: FadeTransition(
                opacity: _fadeAnim,
                child: SlideTransition(
                  position: _slideAnim,
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 420),
                    child: Container(
                      margin: const EdgeInsets.all(24),
                      padding: const EdgeInsets.all(40),
                      decoration: BoxDecoration(
                        color: colors.backgroundSecondary.withValues(
                          alpha: 0.85,
                        ),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(
                          color: Theme.of(
                            context,
                          ).colorScheme.primary.withValues(alpha: 0.2),
                          width: 1,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Theme.of(
                              context,
                            ).colorScheme.primary.withValues(alpha: 0.1),
                            blurRadius: 30,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.vpn_key_rounded,
                              size: 48,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                            const SizedBox(height: 24),
                            Text(
                              "Software Activation",
                              style: Theme.of(context).textTheme.headlineSmall
                                  ?.copyWith(
                                    color: colors.textPrimary,
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              "Enter the License Key assigned to you. This software is bound to your hardware.",
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                color: colors.textSecondary,
                                height: 1.4,
                              ),
                            ),
                            const SizedBox(height: 32),

                            // License Key Input
                            TextFormField(
                              controller: _licenseController,
                              enableInteractiveSelection: true,
                              enabled: !_isLoading,
                              inputFormatters: [UpperCaseTextFormatter()],
                              style: TextStyle(
                                color: colors.textPrimary,
                                letterSpacing: 1.5,
                                fontFamily: 'monospace',
                                fontWeight: FontWeight.bold,
                              ),
                              decoration: InputDecoration(
                                labelText:
                                    "License Key (Format: XXXX-XXXX-XXXX-XXXX)",
                                labelStyle: TextStyle(
                                  color: colors.textSecondary,
                                ),
                                prefixIcon: Icon(
                                  Icons.key,
                                  color: colors.textSecondary,
                                ),
                                filled: true,
                                fillColor: colors.backgroundPrimary.withValues(
                                  alpha: 0.5,
                                ),
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(12),
                                  borderSide: BorderSide(
                                    color: colors.backgroundCard,
                                  ),
                                ),
                                enabledBorder: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(12),
                                  borderSide: BorderSide(
                                    color: colors.backgroundCard,
                                  ),
                                ),
                                focusedBorder: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(12),
                                  borderSide: BorderSide(
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.primary,
                                  ),
                                ),
                              ),
                              validator: (val) {
                                if (val == null || val.trim().isEmpty) {
                                  return "License key is strictly required";
                                }
                                return null;
                              },
                            ),

                            // Error Banner
                            if (_errorMessage != null) ...[
                              const SizedBox(height: 16),
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.error.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.error.withValues(alpha: 0.3),
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    Icon(
                                      Icons.error_outline,
                                      color: Theme.of(
                                        context,
                                      ).colorScheme.error,
                                      size: 20,
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        _errorMessage!,
                                        style: TextStyle(
                                          color: Theme.of(
                                            context,
                                          ).colorScheme.error,
                                          fontSize: 13,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],

                            const SizedBox(height: 32),

                            // Submit Button
                            SizedBox(
                              width: double.infinity,
                              height: 50,
                              child: ElevatedButton(
                                onPressed: _isLoading
                                    ? null
                                    : _handleActivation,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Theme.of(
                                    context,
                                  ).colorScheme.primary,
                                  foregroundColor: Theme.of(
                                    context,
                                  ).colorScheme.onPrimary,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  elevation: 0,
                                ),
                                child: _isLoading
                                    ? SizedBox(
                                        height: 24,
                                        width: 24,
                                        child: CircularProgressIndicator(
                                          color: colors.backgroundPrimary,
                                          strokeWidth: 2,
                                        ),
                                      )
                                    : const Text(
                                        "Activate Machine",
                                        style: TextStyle(
                                          fontSize: 16,
                                          fontWeight: FontWeight.bold,
                                          letterSpacing: 0.5,
                                        ),
                                      ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBackButton(
    BuildContext context,
    WidgetRef ref,
    ThemeColors colors,
  ) {
    final authState = ref.watch(authProvider).asData?.value;
    int trialDays = 0;
    if (authState is AuthUnauthenticated) {
      trialDays = authState.trialDaysRemaining;
    } else if (authState is AuthGuest) {
      trialDays = authState.trialDaysRemaining;
    }

    if (trialDays <= 0) return const SizedBox.shrink();

    return Positioned(
      top: 24,
      left: 24,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => context.go('/dashboard'),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: colors.backgroundSecondary.withValues(alpha: 0.5),
              border: Border.all(
                color: colors.textSecondary.withValues(alpha: 0.3),
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.arrow_back_rounded,
                  color: colors.textSecondary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  "Back to App",
                  style: TextStyle(
                    color: colors.textSecondary,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class UpperCaseTextFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    return TextEditingValue(
      text: newValue.text.toUpperCase(),
      selection: newValue.selection,
    );
  }
}

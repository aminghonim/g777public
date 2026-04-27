import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/semantic_colors.dart';
import '../../features/auth/providers/license_status_provider.dart';

/// SAAS-019: Subscription Expiry Notification Banner.
/// Premium-styled banner that appears at the top of the Dashboard when
/// the license is approaching expiry (7 days or less).
/// When the license is fully expired, it forces redirect to the License Activation page.
class LicenseExpiryBanner extends ConsumerWidget {
  const LicenseExpiryBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final licenseAsync = ref.watch(licenseStatusProvider);

    return licenseAsync.when(
      data: (status) {
        // Guest users or unknown status — no banner needed
        if (status.isGuest ||
            status.reason == 'unknown' ||
            status.reason == 'no_token') {
          return const SizedBox.shrink();
        }

        // License expired or deactivated — force redirect
        if (status.isExpired) {
          // Use addPostFrameCallback to avoid navigating during build
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (context.mounted) {
              context.go('/login');
            }
          });
          return _buildExpiredBanner(context, status);
        }

        // License expiring soon (7 days or less) — show warning
        if (status.isExpiringSoon) {
          return _buildExpiringSoonBanner(context, ref, status);
        }

        // License is valid with plenty of time — no banner
        return const SizedBox.shrink();
      },
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
    );
  }

  Widget _buildExpiringSoonBanner(
    BuildContext context,
    WidgetRef ref,
    LicenseStatus status,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 500),
      curve: Curves.easeInOut,
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: colorScheme.statusWarning.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: colorScheme.statusWarning.withValues(alpha: 0.4),
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: colorScheme.statusWarning.withValues(alpha: 0.15),
            blurRadius: 20,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              _buildPulsingIcon(colorScheme.statusWarning),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'SUBSCRIPTION EXPIRING SOON',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                        color: colorScheme.statusWarning,
                        letterSpacing: 1.5,
                        fontFamily: 'Oxanium',
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Your license expires in ${status.remainingText}. Renew now to ensure uninterrupted service.',
                      style: TextStyle(
                        fontSize: 12,
                        color: colorScheme.onSurfaceVariant,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              _buildRenewButton(context, colorScheme),
            ],
          ),
          const SizedBox(height: 12),
          _buildExpiryProgressBar(colorScheme, status),
        ],
      ),
    );
  }

  Widget _buildExpiredBanner(BuildContext context, LicenseStatus status) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 500),
      curve: Curves.easeInOut,
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: colorScheme.statusError.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: colorScheme.statusError.withValues(alpha: 0.5),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: colorScheme.statusError.withValues(alpha: 0.2),
            blurRadius: 20,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Row(
        children: [
          Icon(
            Icons.lock_outline_rounded,
            color: colorScheme.statusError,
            size: 24,
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'LICENSE EXPIRED',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: colorScheme.statusError,
                    letterSpacing: 2,
                    fontFamily: 'Oxanium',
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  status.reason == 'license_deactivated'
                      ? 'Your license has been deactivated. Please contact support or activate a new license.'
                      : 'Your subscription has expired. Please renew to continue using all features.',
                  style: TextStyle(
                    fontSize: 12,
                    color: colorScheme.onSurfaceVariant,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          _buildRenewButton(context, colorScheme, isExpired: true),
        ],
      ),
    );
  }

  Widget _buildPulsingIcon(Color warningColor) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.6, end: 1.0),
      duration: const Duration(milliseconds: 1200),
      curve: Curves.easeInOut,
      builder: (context, value, child) {
        return Icon(
          Icons.warning_amber_rounded,
          color: warningColor.withValues(alpha: value),
          size: 28,
        );
      },
      onEnd: () {}, // Re-triggers by parent rebuild
    );
  }

  Widget _buildRenewButton(
    BuildContext context,
    ColorScheme colorScheme, {
    bool isExpired = false,
  }) {
    return Material(
      color: isExpired
          ? colorScheme.statusError.withValues(alpha: 0.2)
          : colorScheme.statusWarning.withValues(alpha: 0.2),
      borderRadius: BorderRadius.circular(10),
      child: InkWell(
        borderRadius: BorderRadius.circular(10),
        onTap: () => context.go('/login'),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                isExpired ? Icons.vpn_key_rounded : Icons.autorenew_rounded,
                size: 16,
                color: isExpired
                    ? colorScheme.statusError
                    : colorScheme.statusWarning,
              ),
              const SizedBox(width: 6),
              Text(
                isExpired ? 'ACTIVATE' : 'RENEW',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                  color: isExpired
                      ? colorScheme.statusError
                      : colorScheme.statusWarning,
                  fontFamily: 'Oxanium',
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildExpiryProgressBar(
    ColorScheme colorScheme,
    LicenseStatus status,
  ) {
    // Show progress: 30 days = full, 0 days = empty
    final daysRemaining = status.daysRemaining ?? 0;
    final progress = (daysRemaining / 30).clamp(0.0, 1.0);
    final isUrgent = daysRemaining <= 3;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: progress,
            minHeight: 4,
            backgroundColor: colorScheme.outline.withValues(alpha: 0.15),
            valueColor: AlwaysStoppedAnimation<Color>(
              isUrgent ? colorScheme.statusError : colorScheme.statusWarning,
            ),
          ),
        ),
        const SizedBox(height: 6),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              isUrgent ? 'URGENT: Renew immediately!' : 'Time remaining',
              style: TextStyle(
                fontSize: 10,
                color: isUrgent
                    ? colorScheme.statusError
                    : colorScheme.onSurfaceVariant,
                fontWeight: isUrgent ? FontWeight.bold : FontWeight.normal,
              ),
            ),
            Text(
              '${status.remainingText} left',
              style: TextStyle(
                fontSize: 10,
                color: isUrgent
                    ? colorScheme.statusError
                    : colorScheme.statusWarning,
                fontWeight: FontWeight.bold,
                fontFamily: 'Oxanium',
              ),
            ),
          ],
        ),
      ],
    );
  }
}

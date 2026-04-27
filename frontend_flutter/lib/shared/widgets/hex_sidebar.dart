import 'package:g777_client/core/theme/theme_extensions.dart';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:g777_client/core/theme/semantic_colors.dart';
import 'dart:math' as math;
import 'package:go_router/go_router.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'package:g777_client/l10n/app_localizations_en.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/features/auth/providers/auth_provider.dart';

class G777Sidebar extends ConsumerWidget {
  const G777Sidebar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final extension = theme.extension<G777ThemeExtension>();
    final l10n = AppLocalizations.of(context) ?? AppLocalizationsEn();

    final double blur = extension?.glassBlur ?? 0.0;
    final double opacity = extension?.glassOpacity ?? 1.0;
    final glow = extension?.glowColor;

    Widget sidebarContent = Container(
      width: 240, // Slightly wider for categories
      decoration: BoxDecoration(
        color: colorScheme.sidebarBackground.withValues(alpha: opacity),
        border: Border(
          right: BorderSide(color: colorScheme.sidebarBorder, width: 1),
        ),
        boxShadow: glow != null
            ? [
                BoxShadow(
                  color: glow.withValues(alpha: 0.15),
                  blurRadius: extension?.glowIntensity ?? 10.0,
                  spreadRadius: 2,
                ),
              ]
            : null,
      ),
      child: Column(
        children: [
          const SizedBox(height: 30),
          _buildLogo(colorScheme.sidebarLogo),
          const SizedBox(height: 30),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: [
                // DASHBOARD AT TOP
                _buildHexGrid([
                  _NavItemData(
                    label: l10n.navCloud,
                    imagePath: 'assets/icons/hex/cloud_server.png',
                    color: colorScheme.navCloud,
                    onTap: () => context.go('/dashboard'),
                  ),
                ]),
                const SizedBox(height: 20),

                // CATEGORY A: ADVANCED SENDER
                _buildCategoryHeader(
                  l10n.catAdvancedSender,
                  colorScheme.navAdvancedSender,
                ),
                _buildHexItem(
                  l10n.navSender,
                  'assets/icons/hex/crm_core.png',
                  colorScheme.navAdvancedSender,
                  () => context.go('/group-sender'),
                ),

                const SizedBox(height: 20),
                // CATEGORY B: GROUP TOOLS
                _buildCategoryHeader(
                  l10n.catGroupTools,
                  colorScheme.navGroupTools,
                ),
                _buildHexGrid([
                  _NavItemData(
                    label: l10n.lblMembersGrabber,
                    imagePath: 'assets/icons/hex/maps_extractor.png',
                    color: colorScheme.navGroupTools,
                    onTap: () => context.go('/members-grabber'),
                  ),
                  _NavItemData(
                    label: l10n.lblLinksGrabber,
                    imagePath: 'assets/icons/hex/refined_icon_03.png',
                    color: colorScheme.navGroupTools,
                    onTap: () => context.go('/links-grabber'),
                  ),
                ]),

                const SizedBox(height: 20),
                // CATEGORY C: DATA TOOLS
                _buildCategoryHeader(
                  l10n.catDataTools,
                  colorScheme.navDataTools,
                ),
                _buildHexGrid([
                  _NavItemData(
                    label: l10n.lblGoogleMaps,
                    imagePath: 'assets/icons/hex/maps_extractor.png',
                    color: colorScheme.navDataTools,
                    onTap: () => context.go('/maps-extractor'),
                  ),
                  _NavItemData(
                    label: l10n.lblSocialMedia,
                    imagePath: 'assets/icons/hex/opportunity_hunter.png',
                    color: colorScheme.navDataTools,
                    onTap: () => context.go('/opportunity-hunter'),
                  ),
                  _NavItemData(
                    label: 'Group Finder',
                    imagePath: 'assets/icons/hex/maps_extractor.png',
                    color: colorScheme.navDataTools,
                    onTap: () => context.go('/group-finder'),
                  ),
                ]),

                const SizedBox(height: 20),
                // CATEGORY D: UTILITIES
                _buildCategoryHeader(
                  l10n.catUtilities,
                  colorScheme.navUtilities,
                ),
                _buildHexGrid([
                  _NavItemData(
                    label: l10n.navFilter,
                    imagePath: 'assets/icons/hex/refined_icon_01.png',
                    color: colorScheme.navUtilities,
                    onTap: () => context.go('/number-filter'),
                  ),
                  _NavItemData(
                    label: l10n.navWarmer,
                    imagePath: 'assets/icons/hex/refined_icon_01.png',
                    color: colorScheme.navUtilities,
                    onTap: () => context.go('/warmer'),
                  ),
                  _NavItemData(
                    label: l10n.navPoll,
                    imagePath: 'assets/icons/hex/refined_icon_02.png',
                    color: colorScheme.navUtilities,
                    onTap: () => context.go('/poll-sender'),
                  ),
                  _NavItemData(
                    label: l10n.lblOppHunter,
                    imagePath: 'assets/icons/hex/opportunity_hunter.png',
                    color: colorScheme.navUtilities,
                    onTap: () => context.go('/opportunity-hunter'),
                  ),
                ]),

                const SizedBox(height: 30),
                const Divider(height: 1),
                const SizedBox(height: 10),

                _buildHexGrid([
                  _NavItemData(
                    label: l10n.navBusiness,
                    imagePath: 'assets/icons/hex/business_settings.png',
                    color: colorScheme.navSettings,
                    onTap: () => context.go('/settings'),
                  ),
                  _NavItemData(
                    label: 'خروج', // Fallback if l10n missing
                    iconData: Icons.logout_rounded,
                    color: colorScheme.statusError,
                    onTap: () => ref.read(authProvider.notifier).logout(),
                  ),
                ]),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ],
      ),
    );

    if (blur > 0) {
      return ClipRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
          child: sidebarContent,
        ),
      );
    }

    return sidebarContent;
  }

  Widget _buildCategoryHeader(String label, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, top: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w900,
              color: color.withValues(alpha: 0.8),
              letterSpacing: 1.5,
              fontFamily: 'Oxanium',
            ),
          ),
          Container(
            height: 2,
            width: 40,
            margin: const EdgeInsets.only(top: 4),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.3),
              borderRadius: BorderRadius.circular(1),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHexItem(
    String label,
    String icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Center(
        child: HexNavItem(
          imagePath: icon,
          label: label,
          glowColor: color,
          onTap: onTap,
        ),
      ),
    );
  }

  Widget _buildHexGrid(List<_NavItemData> items) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 10,
        crossAxisSpacing: 10,
        childAspectRatio: 0.85,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return HexNavItem(
          imagePath: item.imagePath,
          iconData: item.iconData,
          label: item.label,
          glowColor: item.color,
          onTap: item.onTap,
        );
      },
    );
  }

  Widget _buildLogo(Color primaryColor) {
    return Column(
      children: [
        Text(
          'G777',
          style: TextStyle(
            color: primaryColor,
            fontSize: 36,
            fontWeight: FontWeight.w900,
            fontFamily: 'Oxanium',
            letterSpacing: 2,
            shadows: [
              Shadow(
                color: primaryColor.withValues(alpha: 0.5),
                blurRadius: 10,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _NavItemData {
  final String label;
  final String? imagePath;
  final IconData? iconData; // Support Flutter Icons
  final Color color;
  final VoidCallback onTap;

  _NavItemData({
    required this.label,
    required this.color,
    required this.onTap,
    this.imagePath,
    this.iconData,
  });
}

class HexNavItem extends StatefulWidget {
  final String? imagePath;
  final IconData? iconData;
  final String label;
  final Color glowColor;
  final VoidCallback? onTap;

  const HexNavItem({
    super.key,
    required this.label,
    required this.glowColor,
    this.imagePath,
    this.iconData,
    this.onTap,
  });

  @override
  State<HexNavItem> createState() => _HexNavItemState();
}

class _HexNavItemState extends State<HexNavItem>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 200),
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.1,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOut));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final extension = theme.extension<G777ThemeExtension>();
    return MouseRegion(
      onEnter: (_) {
        setState(() => _isHovered = true);
        _controller.forward();
      },
      onExit: (_) {
        setState(() => _isHovered = false);
        _controller.reverse();
      },
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: widget.onTap,
        child: ScaleTransition(
          scale: _scaleAnimation,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              SizedBox(
                width: 65,
                height: 65,
                child: CustomPaint(
                  painter: HexagonPainter(
                    borderColor: widget.glowColor,
                    fillColor: _isHovered
                        ? widget.glowColor.withValues(alpha: 0.15)
                        : theme.colorScheme.onSurface.withValues(alpha: 0.05),
                    glow: _isHovered,
                    glowIntensity: extension?.glowIntensity ?? 10.0,
                  ),
                  child: Center(
                    child: ClipPath(
                      clipper: HexagonClipper(),
                      child: widget.iconData != null
                          ? Icon(
                              widget.iconData,
                              size: 28,
                              color: _isHovered
                                  ? widget.glowColor
                                  : theme.colorScheme.onSurface.withValues(
                                      alpha: 0.6,
                                    ),
                            )
                          : Image.asset(
                              widget.imagePath!,
                              width: 32,
                              height: 32,
                              fit: BoxFit.contain,
                              color: _isHovered
                                  ? widget.glowColor
                                  : theme.colorScheme.onSurface.withValues(
                                      alpha: 0.6,
                                    ),
                              colorBlendMode: BlendMode.srcIn,
                            ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 10),
              Flexible(
                child: Text(
                  widget.label,
                  textAlign: TextAlign.center,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: _isHovered
                        ? widget.glowColor
                        : theme.colorScheme.onSurface.withValues(alpha: 0.8),
                    fontSize: 9, // Slightly smaller for long labels
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.5,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class HexagonPainter extends CustomPainter {
  final Color borderColor;
  final Color fillColor;
  final bool glow;
  final double glowIntensity;

  HexagonPainter({
    required this.borderColor,
    required this.fillColor,
    this.glow = false,
    this.glowIntensity = 10.0,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;
    final path = Path();

    for (int i = 0; i < 6; i++) {
      double angle = (i * 60 - 30) * math.pi / 180;
      double x = center.dx + radius * math.cos(angle);
      double y = center.dy + radius * math.sin(angle);
      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    path.close();

    // Draw Glow
    if (glow && glowIntensity > 0) {
      final glowPaint = Paint()
        ..color = borderColor.withValues(alpha: 0.3)
        ..maskFilter = MaskFilter.blur(BlurStyle.outer, glowIntensity);
      canvas.drawPath(path, glowPaint);
    }

    // Draw Border
    final borderPaint = Paint()
      ..color = borderColor.withValues(alpha: glow ? 1.0 : 0.5)
      ..style = PaintingStyle.stroke
      ..strokeWidth = glow ? 2.5 : 1.5;
    canvas.drawPath(path, borderPaint);

    // Draw Fill
    final fillPaint = Paint()
      ..color = fillColor
      ..style = PaintingStyle.fill;
    canvas.drawPath(path, fillPaint);
  }

  @override
  bool shouldRepaint(covariant HexagonPainter oldDelegate) {
    return oldDelegate.glow != glow ||
        oldDelegate.borderColor != borderColor ||
        oldDelegate.fillColor != fillColor;
  }
}

class HexagonClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;
    final path = Path();

    for (int i = 0; i < 6; i++) {
      double angle = (i * 60 - 30) * math.pi / 180;
      double x = center.dx + radius * math.cos(angle);
      double y = center.dy + radius * math.sin(angle);
      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    path.close();
    return path;
  }

  @override
  bool shouldReclip(CustomClipper<Path> oldClipper) => false;
}

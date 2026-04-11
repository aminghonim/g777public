import 'package:flutter/material.dart';

/// Semantic colors mapped securely from the current Theme's ColorScheme.
/// This forms the architectural foundation for Phase 1 of the THEME_FIX_PLAN,
/// removing the need for hardcoded colors in the UI widgets while supporting
/// multiple theme variants (Neon, Professional, Industrial, Modern Glass).
extension G777SemanticColors on ColorScheme {
  // ---------------------------------------------------------------------------
  // Sidebar & Navigation
  // ---------------------------------------------------------------------------
  Color get sidebarBackground => surfaceContainerHighest;
  Color get sidebarItemActive => primary.withValues(alpha: 0.15);
  Color get sidebarItemInactive => onSurface.withValues(alpha: 0.3);
  Color get sidebarTextActive => primary;
  Color get sidebarTextInactive => onSurface.withValues(alpha: 0.6);
  Color get sidebarAccent => primary;
  Color get sidebarBorder => outlineVariant.withValues(alpha: 0.2);
  Color get sidebarLogo => primary;
  Color get dashboardAccent => primary;

  // Sidebar Categories (Functional colors replacing hardcoded assumed names)
  Color get navCloud => primary;
  Color get navAdvancedSender => secondary;
  Color get navGroupTools => tertiary;
  Color get navDataTools => primary;
  Color get navUtilities => secondary;
  Color get navSettings => onSurfaceVariant;

  // ---------------------------------------------------------------------------
  // Dashboard Layout & Gradients
  // ---------------------------------------------------------------------------
  List<Color> get dashboardGradient {
    return [surface, surfaceContainerLowest];
  }

  Color get cardBackground => surfaceContainer;
  Color get cardBorder => outlineVariant.withValues(alpha: 0.3);
  Color get cardShadow => shadow.withValues(alpha: 0.1);

  // ---------------------------------------------------------------------------
  // Status Indicators
  // ---------------------------------------------------------------------------
  Color get statusOnline => Colors.greenAccent.shade400;
  Color get statusWarning => Colors.orangeAccent.shade400;
  Color get statusError => error;
  Color get statusOffline => onSurface.withValues(alpha: 0.3);
  Color get statusInfo => secondary;

  // ---------------------------------------------------------------------------
  // Analytics & Telemetry
  // ---------------------------------------------------------------------------
  Color get telemetryPrimary => primary;
  Color get telemetrySecondary => secondary;
  Color get telemetryText => onSurface;
  Color get telemetryTextMuted => onSurfaceVariant;
  Color get telemetryBackground => surfaceContainerHigh;
  Color get telemetryGridLine => outlineVariant.withValues(alpha: 0.15);

  // ---------------------------------------------------------------------------
  // Interactive Elements & Inputs
  // ---------------------------------------------------------------------------
  Color get inputBackground => surfaceContainerHighest.withValues(alpha: 0.5);
  Color get inputBorder => outline;
  Color get inputBorderFocused => primary;
  Color get inputPlaceholder => onSurfaceVariant.withValues(alpha: 0.5);

  // ---------------------------------------------------------------------------
  // Special Theme Accents & Effects
  // ---------------------------------------------------------------------------
  Color get accentGlow => primary.withValues(alpha: 0.5);
  Color get glassBorder => onSurface.withValues(alpha: 0.1);
  Color get dividerColor => outlineVariant.withValues(alpha: 0.2);

  // ---------------------------------------------------------------------------
  // Theme Style Preview Colors
  // ---------------------------------------------------------------------------
  Color get styleNeon => const Color(0xFFFF4081);
  Color get styleProfessional => const Color(0xFF2962FF);
  Color get styleIndustrial => const Color(0xFF455A64);
}

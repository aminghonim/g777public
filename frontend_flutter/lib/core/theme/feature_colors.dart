import 'package:flutter/material.dart';

/// G777 Feature Color Tokens
/// Centralized semantic color tokens for feature-specific UI elements.
/// This file ensures ALL feature colors adapt to the current theme,
/// eliminating hardcoded Color(0x...) values in widget files.
///
/// Usage: `Theme.of(context).colorScheme.featureAccent`
/// Or via the G777FeatureColors extension.
extension G777FeatureColors on ColorScheme {
  // ---------------------------------------------------------------------------
  // Sending & Campaign Features
  // ---------------------------------------------------------------------------
  Color get sendSuccess => brightness == Brightness.dark
      ? const Color(0xFF00FF41)
      : const Color(0xFF16A34A);

  Color get sendProgress => brightness == Brightness.dark
      ? const Color(0xFFFACC15)
      : const Color(0xFFCA8A04);

  Color get sendError => error;

  // ---------------------------------------------------------------------------
  // Group Sender
  // ---------------------------------------------------------------------------
  Color get groupSenderAccent =>
      brightness == Brightness.dark ? const Color(0xFFFF00D9) : primary;

  Color get groupSenderBackground => brightness == Brightness.dark
      ? const Color(0xFFFF00D9).withValues(alpha: 0.1)
      : primary.withValues(alpha: 0.08);

  // ---------------------------------------------------------------------------
  // Poll Sender
  // ---------------------------------------------------------------------------
  Color get pollAccent =>
      brightness == Brightness.dark ? const Color(0xFFFF00D9) : tertiary;

  Color get pollCardBackground => brightness == Brightness.dark
      ? const Color(0xFF160A16).withValues(alpha: 0.8)
      : surfaceContainer;

  // ---------------------------------------------------------------------------
  // Links Grabber / Opportunity Hunter
  // ---------------------------------------------------------------------------
  Color get grabberAccent => brightness == Brightness.dark
      ? const Color(0xFFEBCB8B)
      : const Color(0xFFB45309);

  Color get grabberCardBackground => brightness == Brightness.dark
      ? const Color(0xFF1A160F)
      : surfaceContainer;

  // ---------------------------------------------------------------------------
  // Members Grabber
  // ---------------------------------------------------------------------------
  Color get membersAccent =>
      brightness == Brightness.dark ? const Color(0xFF2979FF) : primary;

  // ---------------------------------------------------------------------------
  // Account Warmer
  // ---------------------------------------------------------------------------
  Color get warmerAccent =>
      brightness == Brightness.dark ? const Color(0xFF00F3FF) : primary;

  // ---------------------------------------------------------------------------
  // Number Filter
  // ---------------------------------------------------------------------------
  Color get numberFilterAccent =>
      brightness == Brightness.dark ? const Color(0xFF00F3FF) : secondary;

  // ---------------------------------------------------------------------------
  // Dashboard & Telemetry
  // ---------------------------------------------------------------------------
  Color get dashboardAccent =>
      brightness == Brightness.dark ? const Color(0xFF00F3FF) : primary;

  Color get dashboardCardDark => brightness == Brightness.dark
      ? const Color(0xFF0F0F23)
      : surfaceContainer;

  Color get telemetryGreen => brightness == Brightness.dark
      ? const Color(0xFF00FF41)
      : const Color(0xFF16A34A);

  // ---------------------------------------------------------------------------
  // Settings & Danger Zone
  // ---------------------------------------------------------------------------
  Color get dangerAccent => const Color(0xFFF43F5E);

  Color get dangerBackground => brightness == Brightness.dark
      ? const Color(0xFF1A0A0F)
      : const Color(0xFFFEF2F2);
}

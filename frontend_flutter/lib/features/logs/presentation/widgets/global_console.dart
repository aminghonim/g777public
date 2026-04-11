import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/theme/ui_constants.dart';

/// Log Levels for the Global Console
enum LogLevel { success, info, warning, error }

/// A single log entry model
class GlobalLogEntry {
  final String message;
  final LogLevel level;
  final DateTime timestamp;

  GlobalLogEntry({
    required this.message,
    required this.level,
    required this.timestamp,
  });
}

/// [SAAF PHASE 7] Global Logs Console Widget
/// Adheres to the Cosmic Design System mandates.
class GlobalLogsConsole extends StatelessWidget {
  final List<GlobalLogEntry> logs;
  final VoidCallback onClear;
  final String title;

  const GlobalLogsConsole({
    super.key,
    required this.logs,
    required this.onClear,
    this.title = 'GLOBAL LOGS CONSOLE',
  });

  @override
  Widget build(BuildContext context) {
    // Mandated Design Tokens
    const Color spaceBlue = Color(0xFF091522);
    const Color logCyan = Color(0xFF11DCE8);
    const Color logAmber = Color(0xFFFFC107);
    const Color logRed = Colors.redAccent;

    return Container(
      decoration: const BoxDecoration(
        color: spaceBlue,
        border: Border(
          top: BorderSide(color: AppColors.neonCyan, width: 0.5),
        ),
      ),
      child: Column(
        children: [
          // 1. Header Section
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(
                      Icons.terminal_rounded,
                      color: AppColors.neonCyan,
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Text(
                      title,
                      style: GoogleFonts.figtree(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.5,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
                // "Clear Logs" Button with cornerRadius: 60.0
                ElevatedButton.icon(
                  onPressed: onClear,
                  icon: const Icon(Icons.delete_sweep_rounded, size: 16),
                  label: Text(
                    'CLEAR LOGS',
                    style: GoogleFonts.figtree(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white.withValues(alpha: 0.05),
                    foregroundColor: Colors.white70,
                    elevation: 0,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(60.0),
                      side: BorderSide(
                        color: Colors.white.withValues(alpha: 0.1),
                      ),
                    ),
                  ).copyWith(
                    overlayColor: WidgetStateProperty.all(
                      AppColors.neonCyan.withValues(alpha: 0.1),
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          const Divider(height: 1, color: Colors.white10),

          // 2. Log Stream Section
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(16.0),
              child: ListView.builder(
                physics: const BouncingScrollPhysics(),
                itemCount: logs.length,
                itemBuilder: (context, index) {
                  final log = logs[index];
                  Color logColor;
                  String prefix = '●';

                  switch (log.level) {
                    case LogLevel.success:
                      logColor = logCyan;
                      prefix = '✓';
                      break;
                    case LogLevel.info:
                      logColor = logAmber;
                      prefix = 'ℹ';
                      break;
                    case LogLevel.warning:
                      logColor = logAmber;
                      prefix = '⚠';
                      break;
                    case LogLevel.error:
                      logColor = logRed;
                      prefix = '✖';
                      break;
                  }

                  return Padding(
                    padding: const EdgeInsets.only(bottom: 6.0),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Timestamp in Muted Color
                        Text(
                          '[${log.timestamp.hour.toString().padLeft(2, '0')}:${log.timestamp.minute.toString().padLeft(2, '0')}:${log.timestamp.second.toString().padLeft(2, '0')}] ',
                          style: GoogleFonts.jetBrainsMono(
                            color: Colors.white24,
                            fontSize: 11,
                          ),
                        ),
                        // Status Icon/Prefix
                        Text(
                          '$prefix ',
                          style: TextStyle(
                            color: logColor.withValues(alpha: 0.7),
                            fontSize: 12,
                          ),
                        ),
                        // Log Message
                        Expanded(
                          child: Text(
                            log.message,
                            style: GoogleFonts.jetBrainsMono(
                              color: logColor,
                              fontSize: 12,
                              height: 1.4,
                              letterSpacing: -0.2,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}

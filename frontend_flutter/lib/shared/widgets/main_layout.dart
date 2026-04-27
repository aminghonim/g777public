import 'package:flutter/material.dart';
import 'package:g777_client/shared/widgets/hex_sidebar.dart';
import 'package:g777_client/shared/widgets/global_navbar.dart';
import 'package:g777_client/shared/widgets/global_logs_console.dart';

class MainLayout extends StatelessWidget {
  final Widget child;

  const MainLayout({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      body: Row(
        children: [
          // 1. Permanent Sidebar
          const G777Sidebar(),

          // 2. Main Content Area (Navbar + Body + Console)
          Expanded(
            child: Column(
              children: [
                // Top Navbar
                const GlobalNavbar(),

                // Dynamic Page Content
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: RadialGradient(
                        center: Alignment.center,
                        radius: 1.5,
                        colors: [
                          theme.scaffoldBackgroundColor.withValues(alpha: 0.8),
                          theme.scaffoldBackgroundColor,
                        ],
                      ),
                    ),
                    child: child,
                  ),
                ),

                // Interactive Global Logs Console
                const GlobalLogsConsole(),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

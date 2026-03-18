import 'package:flutter/material.dart';
import 'package:g777_client/core/services/api_service.dart';

/// Simple test widget to verify backend connectivity
class ApiTestWidget extends StatefulWidget {
  const ApiTestWidget({super.key});

  @override
  State<ApiTestWidget> createState() => _ApiTestWidgetState();
}

class _ApiTestWidgetState extends State<ApiTestWidget> {
  final ApiService _api = ApiService();
  String _status = 'Not tested yet';
  bool _isLoading = false;

  Future<void> _testConnection() async {
    setState(() {
      _isLoading = true;
      _status = 'Testing...';
    });

    try {
      final health = await _api.checkHealth();
      setState(() {
        _status =
            '✅ Connected!\n'
            'Status: ${health['status']}\n'
            'Version: ${health['version']}\n'
            'Mode: ${health['mode']}';
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _status = '❌ Connection Failed:\n$e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: isDark
            ? const Color(0xFF0F0F23).withValues(alpha: 0.8)
            : theme.cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isDark
              ? const Color(0xFF00F3FF).withValues(alpha: 0.3)
              : colorScheme.primary.withValues(alpha: 0.1),
          width: 1,
        ),
        boxShadow: isDark
            ? [
                BoxShadow(
                  color: const Color(0xFF00F3FF).withValues(alpha: 0.05),
                  blurRadius: 10,
                  spreadRadius: 2,
                ),
              ]
            : null,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'BACKEND CONNECTION TEST',
                style: theme.textTheme.labelSmall?.copyWith(
                  letterSpacing: 2,
                  fontWeight: FontWeight.bold,
                  color: isDark ? const Color(0xFF00F3FF) : colorScheme.primary,
                ),
              ),
              if (!_isLoading && _status.contains('Connected'))
                _buildPulseIndicator(const Color(0xFF00FF41))
              else if (_isLoading)
                _buildPulseIndicator(
                  isDark ? const Color(0xFF00F3FF) : colorScheme.primary,
                )
              else if (_status.contains('Failed'))
                _buildPulseIndicator(Colors.redAccent),
            ],
          ),
          const SizedBox(height: 24),
          if (_status == 'Not tested yet')
            Center(
              child: Text(
                'INITIALIZE TELEMETRY',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurface.withValues(alpha: 0.4),
                ),
              ),
            )
          else
            _buildStatusDisplay(theme, isDark),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _testConnection,
              style: ElevatedButton.styleFrom(
                backgroundColor: isDark
                    ? const Color(0xFF00F3FF).withValues(alpha: 0.1)
                    : colorScheme.primary,
                foregroundColor: isDark
                    ? const Color(0xFF00F3FF)
                    : Colors.white,
                side: isDark
                    ? const BorderSide(color: Color(0xFF00F3FF))
                    : null,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: _isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Color(0xFF00F3FF),
                      ),
                    )
                  : const Text(
                      'RUN DIAGNOSTIC',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.2,
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPulseIndicator(Color color) {
    return Container(
      width: 8,
      height: 8,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.5),
            blurRadius: 8,
            spreadRadius: 2,
          ),
        ],
      ),
    );
  }

  Widget _buildStatusDisplay(ThemeData theme, bool isDark) {
    if (_status.contains('Failed')) {
      return Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.redAccent.withValues(alpha: 0.05),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          _status,
          style: theme.textTheme.bodySmall?.copyWith(
            color: Colors.redAccent,
            fontFamily: 'monospace',
          ),
        ),
      );
    }

    final lines = _status.split('\n');
    return Column(
      children: lines.map((line) {
        if (line.contains(':')) {
          final parts = line.split(':');
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  parts[0].trim().toUpperCase(),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
                  ),
                ),
                Text(
                  parts[1].trim(),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: isDark ? const Color(0xFF00FF41) : Colors.green,
                    fontFamily: 'monospace',
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          );
        }
        return const SizedBox.shrink();
      }).toList(),
    );
  }
}

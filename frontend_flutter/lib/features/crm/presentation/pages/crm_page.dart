import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

import 'package:g777_client/core/theme/theme.dart';
import '../../providers/crm_provider.dart';
import '../../data/crm_repository.dart';

class CrmCustomersPage extends ConsumerWidget {
  const CrmCustomersPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDark = colorScheme.brightness == Brightness.dark;
    final themeColors = AppTheme.getThemeColors(isDark);
    
    final customersState = ref.watch(customersProvider);
    final statsState = ref.watch(crmStatsProvider);

    return Scaffold(
      backgroundColor: themeColors.backgroundPrimary,
      appBar: AppBar(
        title: Text('إدارة العملاء', style: TextStyle(color: themeColors.textPrimary)),
        backgroundColor: themeColors.backgroundSecondary,
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(Icons.refresh, color: themeColors.textPrimary),
            onPressed: () {
              ref.read(customersProvider.notifier).fetchCustomers();
              ref.read(crmStatsProvider.notifier).fetchStats();
            },
            tooltip: 'تحديث الداتا',
          ),
          const SizedBox(width: 8),
          ElevatedButton.icon(
            icon: const Icon(Icons.download, size: 18),
            label: const Text('تصدير CSV'),
            style: ElevatedButton.styleFrom(
              backgroundColor: colorScheme.primary,
              foregroundColor: colorScheme.onPrimary,
            ),
            onPressed: () => _exportCsv(ref, context),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Column(
        children: [
          _buildStatsCards(statsState, themeColors),
          Expanded(
            child: _buildCustomersTable(customersState, themeColors, colorScheme, ref),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsCards(AsyncValue<Map<String, dynamic>> state, ThemeColors colors) {
    return state.when(
      loading: () => const LinearProgressIndicator(),
      error: (e, _) => Padding(
        padding: const EdgeInsets.all(8.0),
        child: Text('خطأ في تحميل الإحصائيات: $e', style: const TextStyle(color: Colors.red)),
      ),
      data: (stats) {
        return Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _StatCard(title: 'إجمالي العملاء', count: stats['total_customers'] ?? 0, colors: colors),
              _StatCard(title: 'عملاء محتملين', count: stats['by_type']?['lead'] ?? 0, colors: colors),
              _StatCard(title: 'عملاء VIP', count: stats['by_type']?['vip'] ?? 0, colors: colors),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCustomersTable(AsyncValue<List<dynamic>> state, ThemeColors colors, ColorScheme colorScheme, WidgetRef ref) {
    return state.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('خطأ: $e', style: const TextStyle(color: Colors.red))),
      data: (customers) {
        if (customers.isEmpty) {
          return Center(child: Text('لا يوجد عملاء', style: TextStyle(color: colors.textMuted)));
        }

        return Card(
          margin: const EdgeInsets.all(16.0),
          color: colors.backgroundCard,
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              headingRowColor: WidgetStateProperty.all(colors.backgroundCard.withValues(alpha: 0.8)),
              columns: [
                DataColumn(label: Text('الاسم', style: TextStyle(color: colors.textPrimary, fontWeight: FontWeight.bold))),
                DataColumn(label: Text('رقم الهاتف', style: TextStyle(color: colors.textPrimary, fontWeight: FontWeight.bold))),
                DataColumn(label: Text('النوع', style: TextStyle(color: colors.textPrimary, fontWeight: FontWeight.bold))),
                DataColumn(label: Text('المدينة', style: TextStyle(color: colors.textPrimary, fontWeight: FontWeight.bold))),
                DataColumn(label: Text('تاريخ الإضافة', style: TextStyle(color: colors.textPrimary, fontWeight: FontWeight.bold))),
              ],
              rows: customers.map((c) => DataRow(
                cells: [
                  DataCell(Text(c['name'] ?? 'بدون اسم', style: TextStyle(color: colors.textPrimary))),
                  DataCell(Text(c['phone'] ?? '-', style: TextStyle(color: colors.textPrimary))),
                  DataCell(_buildTypeBadge(c['customer_type'], colors, colorScheme)),
                  DataCell(Text(c['city'] ?? '-', style: TextStyle(color: colors.textPrimary))),
                  DataCell(Text(
                    c['created_at'] != null 
                        ? DateFormat('yyyy-MM-dd').format(DateTime.parse(c['created_at']))
                        : '-', 
                    style: TextStyle(color: colors.textMuted)
                  )),
                ],
              )).toList(),
            ),
          ),
        );
      },
    );
  }

  Widget _buildTypeBadge(String? type, ThemeColors colors, ColorScheme colorScheme) {
    Color badgeColor;
    String label = type ?? 'غير محدد';
    
    switch (type) {
      case 'vip':
        badgeColor = Colors.purple;
        break;
      case 'lead':
        badgeColor = Colors.orange;
        break;
      case 'customer':
        badgeColor = Colors.green;
        break;
      default:
        badgeColor = colorScheme.primary;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: badgeColor.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: badgeColor.withValues(alpha: 0.5)),
      ),
      child: Text(
        label.toUpperCase(),
        style: TextStyle(color: badgeColor, fontSize: 12, fontWeight: FontWeight.bold),
      ),
    );
  }

  Future<void> _exportCsv(WidgetRef ref, BuildContext context) async {
    try {
      final repository = ref.read(crmRepositoryProvider);
      final url = await repository.getExportUrl();
      final uri = Uri.parse(url);
      
      if (!await launchUrl(uri)) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('فشل فتح رابط التحميل')),
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطأ: $e')),
        );
      }
    }
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final int count;
  final ThemeColors colors;

  const _StatCard({required this.title, required this.count, required this.colors});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: colors.backgroundCard,
      elevation: 2,
      child: Container(
        width: 150,
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(title, style: TextStyle(color: colors.textMuted, fontSize: 14)),
            const SizedBox(height: 8),
            Text(
              count.toString(),
              style: TextStyle(color: AppColors.neonCyan, fontSize: 24, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}

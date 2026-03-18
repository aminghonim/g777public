import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:g777_client/core/services/api_client.dart';
import 'package:g777_client/l10n/app_localizations.dart';
import 'package:g777_client/core/theme/theme.dart'; // Unified theme system

class MembersGrabberPage extends ConsumerStatefulWidget {
  const MembersGrabberPage({super.key});

  @override
  ConsumerState<MembersGrabberPage> createState() => _MembersGrabberPageState();
}

class _MembersGrabberPageState extends ConsumerState<MembersGrabberPage> {
  bool _isLoading = false;
  List<dynamic> _groups = [];
  List<dynamic> _members = [];
  String? _selectedGroupName;

  ApiClient get _api => ref.read(apiClientProvider);

  Future<void> _fetchGroups() async {
    setState(() => _isLoading = true);
    try {
      final res = await _api.get('/api/members-grabber/groups');
      setState(() {
        _groups = res.data as List<dynamic>;
        _isLoading = false;
      });
    } catch (e) {
      _showError('Fetch Groups Error: $e');
    }
  }

  Future<void> _fetchMembers(String jid, String name) async {
    setState(() {
      _isLoading = true;
      _selectedGroupName = name;
    });
    try {
      final res = await _api.get('/api/members-grabber/groups/$jid/members');
      setState(() {
        _members = res.data as List<dynamic>;
        _isLoading = false;
      });
    } catch (e) {
      _showError('Fetch Members Error: $e');
    }
  }

  Future<void> _exportMembers() async {
    if (_members.isEmpty) return;
    setState(() => _isLoading = true);
    try {
      final res = await _api.post(
        '/api/members-grabber/export',
        body: _members,
      );
      if (res.isSuccess) {
        _showSuccess('Members exported successfully: ${res.data['filename']}');
      }
    } catch (e) {
      _showError('Export Error: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showError(String msg) {
    if (!mounted) return;
    setState(() => _isLoading = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg),
        backgroundColor: Theme.of(context).colorScheme.error,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _showSuccess(String msg) {
    if (!mounted) return;
    final colorScheme = Theme.of(context).colorScheme;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg),
        backgroundColor: colorScheme.statusOnline,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(l10n, colorScheme),
          const SizedBox(height: 24),
          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  flex: 2,
                  child: _buildGroupsConsole(l10n, colorScheme),
                ),
                const SizedBox(width: 24),
                Expanded(
                  flex: 3,
                  child: _buildMembersConsole(l10n, colorScheme),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(AppLocalizations l10n, ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.dataGrabber.toUpperCase(),
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: colorScheme.membersAccent,
            letterSpacing: 2,
            fontFamily: 'Oxanium',
            shadows: [Shadow(color: colorScheme.membersAccent, blurRadius: 10)],
          ),
        ),
        Text(
          l10n.extractMemberDesc,
          style: TextStyle(color: colorScheme.onSurface.withValues(alpha: 0.6)),
        ),
      ],
    );
  }

  Widget _buildGroupsConsole(AppLocalizations l10n, ColorScheme colorScheme) {
    final borderColor = colorScheme.outline.withValues(alpha: 0.1);
    return Container(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainer.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
      ),
      child: Column(
        children: [
          _buildConsoleHeader(
            l10n.targetGroups.toUpperCase(),
            Icons.groups_rounded,
            _fetchGroups,
            colorScheme: colorScheme,
            borderColor: borderColor,
          ),
          Expanded(
            child: ListView.separated(
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: _groups.length,
              separatorBuilder: (context, index) =>
                  Divider(height: 1, color: borderColor),
              itemBuilder: (context, index) {
                final group = _groups[index];
                final isSelected = _selectedGroupName == group['name'];
                return _buildDataTile(
                  title: group['name'] ?? 'UNKNOWN_GROUP',
                  subtitle: group['jid'] ?? 'ID_PENDING',
                  isSelected: isSelected,
                  onTap: () => _fetchMembers(group['jid'], group['name']),
                  accentColor: colorScheme.membersAccent,
                  colorScheme: colorScheme,
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMembersConsole(AppLocalizations l10n, ColorScheme colorScheme) {
    final borderColor = colorScheme.outline.withValues(alpha: 0.1);
    return Container(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainer.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
      ),
      child: Column(
        children: [
          _buildConsoleHeader(
            _selectedGroupName?.toUpperCase() ??
                l10n.membersStream.toUpperCase(),
            Icons.person_search_rounded,
            _members.isEmpty ? null : _exportMembers,
            actionIcon: Icons.download_rounded,
            colorScheme: colorScheme,
            borderColor: borderColor,
          ),
          Expanded(
            child: _isLoading
                ? Center(
                    child: CircularProgressIndicator(
                      color: colorScheme.membersAccent,
                    ),
                  )
                : _members.isEmpty
                ? Center(
                    child: Text(
                      l10n.noDataStreaming.toUpperCase(),
                      style: TextStyle(
                        color: colorScheme.onSurface.withValues(alpha: 0.3),
                        fontSize: 10,
                        letterSpacing: 2,
                      ),
                    ),
                  )
                : ListView.separated(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    itemCount: _members.length,
                    separatorBuilder: (context, index) =>
                        Divider(height: 1, color: borderColor),
                    itemBuilder: (context, index) {
                      final member = _members[index];
                      return _buildDataTile(
                        title: member['name'] ?? 'ANONYMOUS_USER',
                        subtitle: member['phone'] ?? 'NO_PHONE',
                        isSelected: false,
                        onTap: null,
                        accentColor: colorScheme.statusOnline,
                        icon: Icons.alternate_email_rounded,
                        colorScheme: colorScheme,
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildConsoleHeader(
    String title,
    IconData icon,
    VoidCallback? onAction, {
    IconData? actionIcon,
    required ColorScheme colorScheme,
    required Color borderColor,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: borderColor)),
      ),
      child: Row(
        children: [
          Icon(icon, size: 16, color: colorScheme.membersAccent),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
                color: colorScheme.onSurface,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          if (onAction != null)
            IconButton(
              onPressed: onAction,
              icon: Icon(actionIcon ?? Icons.refresh_rounded, size: 16),
              color: colorScheme.membersAccent,
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
            ),
        ],
      ),
    );
  }

  Widget _buildDataTile({
    required String title,
    required String subtitle,
    required bool isSelected,
    required VoidCallback? onTap,
    required Color accentColor,
    required ColorScheme colorScheme,
    IconData? icon,
  }) {
    return InkWell(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected
              ? accentColor.withValues(alpha: 0.05)
              : Colors.transparent,
          border: isSelected
              ? Border(left: BorderSide(color: accentColor, width: 2))
              : null,
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: (isSelected ? accentColor : colorScheme.onSurface)
                    .withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon ?? Icons.hub_rounded,
                size: 14,
                color: isSelected
                    ? accentColor
                    : colorScheme.onSurface.withValues(alpha: 0.5),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: isSelected ? accentColor : colorScheme.onSurface,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 9,
                      color: colorScheme.onSurface.withValues(alpha: 0.4),
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
            ),
            if (isSelected)
              Icon(
                Icons.chevron_right_rounded,
                size: 16,
                color: colorScheme.membersAccent,
              ),
          ],
        ),
      ),
    );
  }
}

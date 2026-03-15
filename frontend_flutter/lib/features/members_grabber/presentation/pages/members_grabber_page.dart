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
  bool _isLoadingMore = false;
  int _currentPage = 0;
  static const int _pageSize = 100;
  bool _hasMorePages = true;
  final ScrollController _scrollController = ScrollController();

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

  Future<void> _fetchMembers(String jid, String name, {bool loadMore = false}) async {
    if (!loadMore) {
      setState(() {
        _isLoading = true;
        _selectedGroupName = name;
        _members.clear();
        _currentPage = 0;
        _hasMorePages = true;
      });
    } else {
      if (_isLoadingMore || !_hasMorePages) return;
      setState(() => _isLoadingMore = true);
    }

    try {
      final page = loadMore ? _currentPage + 1 : 1;
      final res = await _api.get('/api/members-grabber/groups/$jid/members?page=$page&limit=$_pageSize');
      final newMembers = res.data['members'] as List<dynamic>? ?? [];
      final totalCount = res.data['total'] as int? ?? 0;

      // Export all loaded members (paginated)
      setState(() {
        if (!loadMore) {
          _members = newMembers;
        } else {
          _members.addAll(newMembers);
          _currentPage = page;
        }
        _hasMorePages = _members.length < totalCount;
        _isLoading = false;
        _isLoadingMore = false;
      });
    } catch (e) {
      _showError('Fetch Members Error: $e');
      setState(() {
        _isLoading = false;
        _isLoadingMore = false;
      });
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
@override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 200 &&
        !_isLoadingMore &&
        _hasMorePages &&
        _selectedGroupName != null) {
      _fetchMembers(_groups.firstWhere((g) => g['name'] == _selectedGroupName)['jid'], _selectedGroupName!, loadMore: true);
    }),
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
          Expandedkey: ValueKey(group['jid']),
                  (
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
                  Column(
                    children: [
                      Expanded(
                        child: ListView.separated(
                          controller: _scrollController,
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          itemCount: _members.length + (_hasMorePages ? 1 : 0),
                          separatorBuilder: (context, index) =>
                              Divider(height: 1, color: borderColor),
                          itemBuilder: (context, index) {
                            if (index == _members.length) {
                              // Loading indicator for next page
                              return Center(
                                child: Padding(
                                  padding: const EdgeInsets.all(16.0),
                                  child: CircularProgressIndicator(
                                    color: colorScheme.membersAccent,
                                    strokeWidth: 2,
                                  ),
                                ),
                              );
                            }
                            final member = _members[index];
                            return _buildDataTile(
                              key: ValueKey('${member['phone']}_${index}'),
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
                      if (_members.length > _pageSize)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            border: Border(top: BorderSide(color: borderColor)),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                '${l10n.showing} ${_members.length} ${l10n.members.toLowerCase()}',
                                style: TextStyle(
                                  fontSize: 10,
                                  color: colorScheme.onSurface.withValues(alpha: 0.6),
                                ),
                              ),
                              if (_hasMorePages)
                                Text(
                                  l10n.loadMore ?? 'Load More',
                                  style: TextStyle(
                                    fontSize: 10,
                                    color: colorScheme.membersAccent,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                            ],
                          ),
                        ),
                    ] );
                    },
                  ),
          ),
    Key? key,
    required String title,
    required String subtitle,
    required bool isSelected,
    required VoidCallback? onTap,
    required Color accentColor,
    required ColorScheme colorScheme,
    IconData? icon,
  }) {
    return InkWell(
      key: key,nAction, {
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

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../shared/painters/custom_painters.dart';
import '../../providers/auth_provider.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isPasswordVisible = false;
  late AnimationController _animController;
  late Animation<double> _fadeAnim;
  late Animation<Offset> _slideAnim;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _fadeAnim = CurvedAnimation(parent: _animController, curve: Curves.easeOut);
    _slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.08),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _animController, curve: Curves.easeOut));
    _animController.forward();
  }

  @override
  void dispose() {
    _animController.dispose();
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;
    await ref
        .read(authProvider.notifier)
        .login(_usernameController.text.trim(), _passwordController.text);
  }

  Future<void> _handleClerkLogin() async {
    await ref.read(authProvider.notifier).loginWithClerk();
  }

  Future<void> _handleGuestLogin() async {
    await ref.read(authProvider.notifier).continueAsGuest();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final colors = AppTheme.getThemeColors(isDark);

    // Listen for state changes to handle navigation and errors
    ref.listen<AsyncValue<AuthState>>(authProvider, (previous, next) {
      if (next is AsyncData<AuthState>) {
        final state = next.value;
        if (state is AuthAuthenticated || state is AuthGuest) {
          context.go('/dashboard');
        }
      }
    });

    final errorMessage = authState.whenOrNull(
      data: (state) => state is AuthError ? state.message : null,
    );

    return Scaffold(
      backgroundColor: colors.backgroundPrimary,
      body: Stack(
        children: [
          // Ambient background
          CustomPaint(
            painter: CircuitBackgroundPainter(isDark: isDark),
            size: Size.infinite,
          ),
          // Centered login card
          Center(
            child: FadeTransition(
              opacity: _fadeAnim,
              child: SlideTransition(
                position: _slideAnim,
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 420),
                  child: Container(
                    margin: const EdgeInsets.all(24),
                    padding: const EdgeInsets.all(40),
                    decoration: BoxDecoration(
                      color: colors.backgroundSecondary.withValues(alpha: 0.85),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: AppColors.neonCyan.withValues(alpha: 0.3),
                        width: 1,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.neonCyan.withValues(alpha: 0.08),
                          blurRadius: 40,
                          spreadRadius: 5,
                        ),
                      ],
                    ),
                    child: SingleChildScrollView(
                      child: Form(
                        key: _formKey,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // Logo
                            _buildLogo(colors),
                            const SizedBox(height: 36),

                            // Username field
                            _buildTextField(
                              controller: _usernameController,
                              label: 'اسم المستخدم',
                              hint: 'admin',
                              icon: Icons.person_outline_rounded,
                              colors: colors,
                              validator: (v) => (v == null || v.trim().isEmpty)
                                  ? 'مطلوب'
                                  : null,
                            ),
                            const SizedBox(height: 16),

                            // Password field
                            _buildTextField(
                              controller: _passwordController,
                              label: 'كلمة المرور',
                              hint: '••••••••',
                              icon: Icons.lock_outline_rounded,
                              colors: colors,
                              isPassword: true,
                              isPasswordVisible: _isPasswordVisible,
                              onTogglePassword: () => setState(
                                () => _isPasswordVisible = !_isPasswordVisible,
                              ),
                              validator: (v) =>
                                  (v == null || v.isEmpty) ? 'مطلوب' : null,
                            ),
                            const SizedBox(height: 8),

                            // Error message
                            if (errorMessage != null) ...[
                              const SizedBox(height: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 8,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.redAccent.withValues(
                                    alpha: 0.1,
                                  ),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(
                                    color: Colors.redAccent.withValues(
                                      alpha: 0.4,
                                    ),
                                  ),
                                ),
                                child: Text(
                                  errorMessage,
                                  style: TextStyle(
                                    color: Colors.redAccent.shade100,
                                    fontSize: 13,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            ],

                            const SizedBox(height: 28),

                            // Primary: Clerk sign-in (opens system browser)
                            _buildClerkButton(colors),

                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Expanded(
                                  child: Divider(color: colors.textMuted.withValues(alpha: 0.3)),
                                ),
                                Padding(
                                  padding: const EdgeInsets.symmetric(horizontal: 12),
                                  child: Text(
                                    'أو',
                                    style: TextStyle(color: colors.textMuted, fontSize: 12),
                                  ),
                                ),
                                Expanded(
                                  child: Divider(color: colors.textMuted.withValues(alpha: 0.3)),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),

                            // Legacy: local username/password login
                            _buildLoginButton(colors),

                            const SizedBox(height: 16),

                            // Guest Login Button
                            _buildGuestButton(colors),

                            const SizedBox(height: 20),
                            Center(
                              child: Text(
                                'G777 Antigravity - v3.0.0',
                                style: TextStyle(
                                  color: colors.textMuted,
                                  fontSize: 11,
                                  letterSpacing: 1.5,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLogo(ThemeColors colors) {
    return Column(
      children: [
        Text(
          'G777',
          style: TextStyle(
            color: AppColors.neonCyan,
            fontSize: 52,
            fontWeight: FontWeight.bold,
            letterSpacing: 6,
            shadows: [
              Shadow(
                color: AppColors.neonCyan.withValues(alpha: 0.7),
                blurRadius: 24,
              ),
            ],
          ),
        ),
        Text(
          'ULTIMATE',
          style: TextStyle(
            color: colors.textSecondary,
            fontSize: 13,
            letterSpacing: 10,
            fontWeight: FontWeight.w300,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          height: 1,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Colors.transparent,
                AppColors.neonCyan.withValues(alpha: 0.5),
                Colors.transparent,
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    required ThemeColors colors,
    bool isPassword = false,
    bool isPasswordVisible = false,
    VoidCallback? onTogglePassword,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            color: colors.textSecondary,
            fontSize: 12,
            fontWeight: FontWeight.w600,
            letterSpacing: 1,
          ),
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: controller,
          obscureText: isPassword && !isPasswordVisible,
          validator: validator,
          style: TextStyle(color: colors.textPrimary, fontSize: 14),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: TextStyle(color: colors.textMuted, fontSize: 14),
            prefixIcon: Icon(icon, color: AppColors.neonCyan, size: 18),
            suffixIcon: isPassword
                ? IconButton(
                    icon: Icon(
                      isPasswordVisible
                          ? Icons.visibility_off_outlined
                          : Icons.visibility_outlined,
                      color: colors.textMuted,
                      size: 18,
                    ),
                    onPressed: onTogglePassword,
                  )
                : null,
            filled: true,
            fillColor: colors.backgroundPrimary.withValues(alpha: 0.5),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: BorderSide(
                color: AppColors.neonCyan.withValues(alpha: 0.2),
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: BorderSide(
                color: AppColors.neonCyan.withValues(alpha: 0.2),
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: AppColors.neonCyan, width: 1.5),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Colors.redAccent),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 14,
            ),
          ),
          onFieldSubmitted: (_) => _handleLogin(),
        ),
      ],
    );
  }

  Widget _buildLoginButton(ThemeColors colors) {
    final isLoading = ref.watch(authProvider).isLoading;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: isLoading ? null : _handleLogin,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          height: 50,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppColors.neonCyan.withValues(alpha: 0.8),
                AppColors.neonCyan,
              ],
            ),
            borderRadius: BorderRadius.circular(10),
            boxShadow: [
              BoxShadow(
                color: AppColors.neonCyan.withValues(alpha: 0.35),
                blurRadius: 20,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Center(
            child: isLoading
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      color: Colors.black,
                      strokeWidth: 2.5,
                    ),
                  )
                : const Text(
                    'دخول',
                    style: TextStyle(
                      color: Colors.black,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      letterSpacing: 2,
                    ),
                  ),
          ),
        ),
      ),
    );
  }

  Widget _buildClerkButton(ThemeColors colors) {
    final isLoading = ref.watch(authProvider).isLoading;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: isLoading ? null : _handleClerkLogin,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          height: 50,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF6C47FF), Color(0xFF9B72FF)],
            ),
            borderRadius: BorderRadius.circular(10),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF6C47FF).withValues(alpha: 0.35),
                blurRadius: 20,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Center(
            child: isLoading
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      color: Colors.white,
                      strokeWidth: 2.5,
                    ),
                  )
                : const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.lock_open_rounded, color: Colors.white, size: 18),
                      SizedBox(width: 10),
                      Text(
                        'تسجيل الدخول بـ Clerk',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                          letterSpacing: 1,
                        ),
                      ),
                    ],
                  ),
          ),
        ),
      ),
    );
  }

  Widget _buildGuestButton(ThemeColors colors) {
    final isLoading = ref.watch(authProvider).isLoading;
    return TextButton(
      onPressed: isLoading ? null : _handleGuestLogin,
      style: TextButton.styleFrom(
        foregroundColor: colors.textSecondary,
        padding: const EdgeInsets.symmetric(vertical: 16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.no_encryption_gmailerrorred_rounded,
            size: 16,
            color: colors.textMuted,
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              "الدخول المباشر (نسخة تجريبية)",
              style: TextStyle(
                fontSize: 13,
                color: colors.textMuted,
                decoration: TextDecoration.underline,
                decorationColor: colors.textMuted.withValues(alpha: 0.5),
              ),
              overflow: TextOverflow.ellipsis,
              maxLines: 1,
            ),
          ),
        ],
      ),
    );
  }

  // Methods are now simplified and handled via ref.listen/authState
}

# 🧠 Antigravity Project Memory

## 🚀 Core Project State

- **Primary Database**: **Supabase** (PostgreSQL via Pooler).
  - **Database URL**: `postgresql://postgres.zbrpwteyldwpqlcxdpmf:G777SecureCRM2026@aws-1-eu-central-1.pooler.supabase.com:6543/postgres`
- **Supabase Project**: `zbrpwteyldwpqlcxdpmf` (`https://zbrpwteyldwpqlcxdpmf.supabase.co`)
- **AI Model**: **Dynamic Routing** via `ModelRouter` (Gemini 3.1 Flash/Pro + 2.5 Computer Use).
- **Secondary Stack (Modern Free Stack)**:
  - **Email**: **Resend** (Free 3k/mo). `backend/services/resend_client.py`. (API Key: `re_X6N...`)
  - **Vector DB**: **Pinecone** (Serverless `us-east-1`). `backend/services/pinecone_manager.py`. (Rule 12: Tenant isolation enforced).
  - **Cache & Rate Limit**: **Upstash Redis**. `backend/services/cache_manager.py`. (Rule 11: AI Budget protection).
  - **Auth & Identity**: **Clerk**. `backend/core/auth.py`. (Middleware + JWT Verification).
  - **Observability**: **Sentry**. `backend/core/monitoring.py`. (Error & Performance tracking).
- **SAAF Status**: **Full Squad Mode ACTIVATED** (SAAF Governance Enforcement active).
- **Deprecated Database**: **Neon PostgreSQL** (Confirmed Removed).
- **Communication Engine**: **Evolution API v2** (Local/Gateway architecture).
  - **Local Gateway**: `backend/wa_gateway.py` (WAGateway class).
  - **Logic Mixins**: `backend/evolution/` (Handlers for connection, messaging, etc.).
- **Cloud Naming Status**: All legacy 'Cloud' references refactored to 'WA/Evolution' to avoid confusion between local gateway and external cloud.
- **Automation**: **n8n Local** (`http://127.0.0.1:5678`).

## 🛠️ Infrastructure Details (Local: 127.0.0.1)

- **Evolution API Port**: `3000` (Local Bridge).
- **n8n Port**: `5678`.
- **Internal Webhook Gateway**: `http://172.17.0.1:5678/webhook/whatsapp`.
- **Evolution API Key**: `antigravity_secret_key_2024`.

## 🛡️ Critical Operating Rules

1.  **No Neon**: Any reference to Neon/Port 5432 should be avoided.
2.  **Postgres Pooler**: Use Port `6543` for Supabase connection to ensure stability.
3.  **Arabic Communication**: Default technical reasoning and explanations in Arabic.
4.  **Emoji usage**: Forbidden in code blocks.
5.  **SAAF Enforcement**: All AI interventions MUST use `agent-router` (Backend) or `impeccable-protocol` (Frontend). Emergency reset command is `[SAAF ENFORCEMENT - HALT]`.

## 📅 Historical Milestones

- **2026-01-31**: Stabilized Backend Test suite.
- **2026-01-31**: Found and restored real Supabase & Gemini credentials from `البوت_يرد` backup.
- **2026-01-31**: Deleted stale `.env.production` that pointed to Neon.
- **2026-02-26**: Finalized Scrapling Integration with Stealth fetching and Session Injector capabilities for GroupFinder.
- **2026-03-01**: Completed full migration to Linux environment. Fixed Python interpreter paths, removed Windows `.ps1`/`.bat` artifacts, and updated VS Code configurations for cross-platform stability.
- **2026-03-01**: **The Great Refactor**: Renamed all "Cloud" modules to "Evolution/WA Gateway".
  - Moved `backend/cloud/` -> `backend/evolution/`.
  - Renamed `AzureCloudService` -> `WAGateway`.
  - Updated API prefix to `/api/wa-hub`.
  - Integrated backward-compatibility shims to prevent regressions in legacy code.

- **2026-03-07**: **CNS SQUAD ACTIVE**: Activated & merged CodeRabbit AI Audit system into `main`.
  - Repository: `https://github.com/aminghonim/g777public`.
  - Configuration: `.coderabbit.yaml` (Schema v2) with Arabic reviews and CNS Squad quality mandates.
  - PR #1 `fix/test-cns-review` **merged** — 4 commits, 0 regressions, CodeRabbit: "No actionable comments".
  - Local `main` synced via `git pull --rebase origin main`.
  - Future: RAGAS Integration Plan prepared in `Artifacts/RAGAS_Integration_Plan.md`.
- **2026-03-08**: **THE MODERN UNIFICATION**:
  - Consolidated all project rules into a single **CNS Squad Constitution** (`GEMINI.md`).
  - Audited and cleaned `G777_MIGRATION_VAULT`; extracted n8n workflows and recovered `baileys-service` source.
  - Successfully integrated the **Modern Free Stack** (Resend, Pinecone, Upstash, Sentry, Clerk).
  - Implemented **Clerk Authentication Middleware** with a legacy fallback for Zero-Regression (Rule 4).
  - Verified all core managers with a new `pytest` suite: `tests/test_free_stack_managers.py`.

- **2026-03-10**: **NICEGUI PURGE**:
  - Completely removed **NiceGUI** from the project to finalize the transition to **Flutter**.
  - Deleted `ui/` (legacy NiceGUI controllers), NiceGUI-specific tests, and Figma converter.
  - Updated **GEMINI.md**, **.cursor/rules/cns.mdc**, and architectural docs to reflect the Flutter-only frontend.
  - Resolved Python interpreter path issues by standardizing on `.venv` and updating VS Code / MCP configurations.

- **2026-03-11**: **MCP STABILIZATION**:
  - Installed `mcp-python-sdk` in the core virtual environment (`.venv`).
  - Refactored `backend/mcp_manager.py` to fix singleton initialization bugs and linting errors.
  - Implemented lazy logging, explicit UTF-8 encoding, and comprehensive docstrings.
  - Verified MCP tool discovery across all configured servers (GitKraken, postgres, chrome-devtools, etc.).
  - Cleaned up `backend/verify_mcp.py` and confirmed successful discovery test.

- **2026-04-26**: **LICENSE SYSTEM COMPLETION (P0 + P1)**:
  - Fixed port mismatch (Flutter 8001 → 8081).
  - Fixed 401 "Session expired" error: restored `.env.docker.local`, added `/auth/license` prefix to router, added exempt paths.
  - P0: Added Admin Guard on `/auth/license/generate` endpoint.
  - P0: Inserted tier data (Starter, Pro, Enterprise) into DB.
  - P1: Built **License Expiry Middleware (LicenseGuard)** — checks license expiration on every API request.
    - Files modified: `core/middleware.py`, `core/config.py`, `backend/database_manager.py`, `main.py`.
    - `check_license_status()` method in `DatabaseManager` queries `licenses` table.
    - Returns 403 `LICENSE_EXPIRED` with reason + days_expired for expired/deactivated licenses.
    - Bypasses: guest/admin roles, exempt paths (auth, webhooks, health), no-Bearer requests.
    - Fail-open on DB error to avoid blocking all users.
  - Activated real **Upstash Redis** (response time: 30s timeout → 0.55s).
  - Created `customers`, `interactions`, `analytics` tables in Docker Postgres + auto-migration (`_ensure_crm_tables`).
  - Unit tests: 13/13 pass. Live integration tests: 7/7 pass.
  - Test script: `scripts/live_license_guard_test.sh`.

- **2026-04-27**: **SUBSCRIPTION EXPIRY NOTIFICATION (P2)**:
  - Backend: Added `GET /auth/license/status` endpoint in `backend/routers/license.py`.
    - Returns `is_valid`, `reason`, `role`, `expires_at`, `days_remaining`, `days_expired`.
    - Guest users get `guest_access` with no expiry info.
    - Added to `license_exempt_paths` in `core/config.py`.
  - Flutter Provider: `license_status_provider.dart` — `@riverpod` code-gen pattern.
    - `LicenseStatus` model with `isExpiringSoon` (≤7 days), `isExpired`, `isGuest`, `remainingText`.
    - `LicenseStatusNotifier` fetches from `/auth/license/status` via `ApiClient`.
    - Generated `.g.dart` via `build_runner`.
  - Flutter Widget: `license_expiry_banner.dart` — premium-styled `ConsumerWidget`.
    - Warning banner (≤7 days): pulsing icon, progress bar, RENEW button, URGENT label (≤3 days).
    - Expired banner: lock icon, ACTIVATE button, force redirect to `/login` via `addPostFrameCallback`.
    - Hidden for guest/unknown/valid states.
    - Uses `colorScheme.statusWarning` and `colorScheme.statusError` semantic colors.
  - Dashboard integration: `LicenseExpiryBanner()` added to `dashboard_page.dart`.
  - Unit tests: 25/25 pass (`test/unit/license_status_test.dart`).
  - Widget tests: 14/14 pass (`test/widget/license_expiry_banner_test.dart`).
  - Backend rebuilt and endpoint verified live: `{"is_valid":true,"reason":"no_license_bound","role":"admin"}`.

## ⚠️ Known Blockers/Issues

- Evolution API may need `sudo docker restart evolution-api` if webhooks stop arriving.
- **Pydantic Version Conflict**: `clerk-sdk-python` requires `pydantic<2.0.0`, but FastAPI and other core modules require `pydantic>=2.7.0`.
  - **Status**: Clerk SDK uninstalled from pip to keep the system stable. Using a custom manual `ClerkAuth` implementation via `httpx` to avoid version hell.

## 🔴 Technical Pitfalls & Anti-Patterns

- **PowerShell `Remove-Item` (del) Error**:
  - **Error**: `InvalidArgument: (:) [Remove-Item], ParameterBindingException` / `PositionalParameterNotFound`.
  - **Cause**: Using CMD-style flags (like `/q`, `/s`, `/f`) with PowerShell's `del` alias (which maps to `Remove-Item`).
  - **Prevention**: ALWAYS use PowerShell syntax: `Remove-Item -Path "path" -Recurse -Force` instead of `del /q`.
- **Local Dev Connection**:
  - The system uses **Local Baileys Bridge** (Port `3000`) for all communications ensuring faster iteration and privacy.
  - `EvolutionManager` has a "Hybrid Adapter" to auto-detect Port `3000` and switch logic.
- **CodeRabbit YAML Schema Pitfall (`.coderabbit.yaml`):**
  - **Error**: `Expected object, received boolean at "reviews.tools.ruff"` (and any other tool name).
  - **Cause**: Tools must be configured as objects like `{enabled: false}`, NOT as raw booleans (`false`).
  - **Correct**: `ruff:\n  enabled: false`
  - **Wrong**: `ruff: false`
  - **Additional**: `ast-grep` tool uses a completely different schema (`rule_dirs`, `essential_rules`). Do NOT use `enabled: false` for it. Remove it entirely if not needed.
- **Pydantic Version Hell**:
  - **Avoid**: Installing `clerk-sdk-python` via pip (it forces a downgrade to 1.10.x).
  - **Solution**: Use direct API calls to `api.clerk.com` for session verification.
- **Rule Consolidation**:
  - **Rule**: NEVER create scattered `.mdc` or `.md` rules. **GEMINI.md** is the single source of truth (Rule 0).
- **2026-03-11**: **THE SMART TASK ROUTER**:
  - Implemented a centralized **Smart Task Router** (`backend/core/model_router.py`) to move away from hardcoded model names.
  - Configured dynamic selection in `config.yaml` for tasks: `intent_analysis`, `customer_chat`, `extraction`, `computer_use`, `content_generation`.
  - Upgraded core components (`AIEngine`, `Orchestrator`, `GeminiAIClient`) to use the router, enabling **Gemini 3.1 Thinking** and **Visual RPA**.
  - Verified logic and live connectivity with a new surgical test suite.
- **2026-03-14**: **MEDIA & AI STABILIZATION**:
  - Resolved **401 Unauthorized** error for media downloads by bypassing the Backend and connecting n8n directly to `baileys_bridge:3000`.
  - Fixed **404 Missing Endpoint** by injecting a new `/download` route into `baileys-service/server.js` for media decryption.
  - Resolved **Gemini Veo Model Error** in n8n by switching the task from "Generate Video" to "Multimodal Chat" (Analyze) using binary input.
  - Finalized the **Media Decryption Pipeline**: WhatsApp (Encrypted) -> Bridge (Decrypt) -> n8n (Binary) -> Gemini (Analyze).

- **2026-04-08**: **THEME-AGNOSTIC CONSTITUTION**:
  - Executed a critical architecture update to decouple UI Agent from hardcoded themes.
  - Removed "OLED Midnight" mandates and hex `#0a0e27` from `backend/gemini_ui_designer.py`.
  - Injected **Rule 6: Theme-Agnostic Execution** into `COMPLIANCE_PROTOCOL.md`.
  - Established the principle of "Neutral Execution": All styling must be derived from Design Tokens, ensuring support for Dual-Theme (Light/Dark) architecture.
- **2026-04-08**: **PHASE 7 (GLOBAL LOGS CONSOLE)**:
  - Materialized **Cosmic Design System** core theme files from the archive branch.
  - Implemented `GlobalLogsConsole` widget in `lib/features/logs/presentation/widgets/`.
  - Verified UI governance via `flutter analyze` ensuring zero linting errors.
  - Enforced exact **Space Blue** (#091522) and Neon color tokens for the logging interface.

- **2026-04-13**: **SAAF FULL SQUAD ACTIVATION**:
  - Integrated **SAAF (Super AI Agency Framework)** directives into core project memory.
  - Activated mandatory MCP routing for Backend (`agent-router`) and Frontend (`impeccable-protocol`).
  - Updated `GEMINI.md` as the single source of truth for SAAF Governance.
  - Established logic for **SAAF ENFORCEMENT - HALT** to prevent AI hallucinations and unverified code execution.

- **2026-04-14**: **SAAF MODELS REFACTOR**:
  - Performed surgical refactor of `backend/models/group_sender.py` for full CNS Squad compliance.
  - Injected mandatory docstrings and strict type hints (SAAF Rule 8).
  - Enforced **Tenant Isolation** by adding `instance_name` to all persistent models (SAAF Rule 12).
  - Hardened type safety by converting status strings to `BroadcastStatusEnum`.
  - Integrated Pydantic field validation (`ge=0`) for broadcasting delay parameters.
  - Verified logic with an automated TDD-based scratch suite.

- **2026-04-14**: **VULNERABILITY M8 (MCP AUTH) FIXED**:
  - Implemented `backend/core/mcp_auth.py` with `MCPAuthenticator` singleton.
  - Added `X-MCP-Token` header validation using `hmac.compare_digest` for timing-attack protection.
  - Integrated authentication into `MCPManager.call_tool` and `MCPManager.get_tools_definitions`.
  - Enforced mandatory API key check for all MCP tool invocations.
  - Achieved **GREEN** status on security TDD suite `tests/security/test_mcp_auth.py`.

- **2026-04-19**: **VULNERABILITY M7 (UNAUTHENTICATED WEBHOOKS) FIXED**:
  - Implemented `verify_evolution_signature()` as a FastAPI `Depends()` in `backend/webhook_handler.py`.
  - Algorithm: **HMAC-SHA256** over raw request body, verified via `hmac.compare_digest()` (CWE-208 timing-attack protection).
  - Protected endpoints: `POST /webhook/whatsapp` and `POST /api/webhook/evolution`.
  - Fail-closed behavior: missing `EVOLUTION_WEBHOOK_SECRET` env var → HTTP 500; signature mismatch → HTTP 403 + WARNING log with client IP.
  - Unprotected by design: `/webhook/health` (monitoring) and `/webhook/test` (dev-only).
  - New secret required in env: `EVOLUTION_WEBHOOK_SECRET` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`.
  - Achieved **GREEN** status: 5/5 TDD tests passing, 34 pre-existing tests unbroken.
  - Branch `fix/m7-webhook-auth` merged into `cleansed-history` via `--no-ff`.

- **2026-04-19**: **VULNERABILITY M5 (QUOTAGUARD GUEST FALLBACK BYPASS) FIXED**:
  - Root cause: `_get_effective_user_id()` used Python's `or` chain → `user_id or sub or GUEST_USER_ID`, so any falsy value (empty string, None) silently resolved to the guest UUID.
  - **File 1:** `backend/core/quota_guard.py` — replaced silent `or` fallback with an explicit guard: if `user_id` and `sub` are both falsy, raise `HTTPException(401)`.
  - **File 2:** `core/dependencies.py` — eliminated silent `pass` after Clerk rejection; when `CLERK_SECRET_KEY` is configured, a Clerk rejection now immediately re-raises (`raise clerk_exc`). SecurityEngine fallback is only reached when Clerk is NOT configured.
  - Attack vector closed: Attacker can no longer craft a valid-signature JWT with `user_id=""` to bypass per-tenant quota tracking.
  - Real guest path preserved: `/auth/guest` issues tokens with `user_id=GUEST_USER_ID` (non-empty), which passes the guard correctly.
  - Achieved **GREEN** status: 5/5 new TDD tests + 23/23 full security suite passing.
  - Branch `fix/m5-quotaguard-bypass` merged into `cleansed-history` via `--no-ff`.

- **2026-04-19**: **VULNERABILITY M10 (SAFETYPROTOCOL BYPASS) FIXED**:
  - Root cause: `validate_code_safety()` defaulted to `True` for unknown/non-Python languages. Orchestrator passed `shell` identifier which was silently approved and ignored.
  - Agent Router Issue fixed: `agent_router.py` was causing `context canceled` due to a 14s retry loop on missing `PINECONE_HOST`. Fixed tenacity import and logic.
  - **File 1:** `backend/core/safety.py` — Strictly enforced `Fail-closed` behavior. Added `SUPPORTED_LANGUAGES = {"python"}` and rejected anything else with `HTTPException(401)`/False.
  - **File 2:** `backend/agents/orchestrator.py` — Replaced the silent `pass` with actual execution blocking if shell command is rejected by `SafetyProtocol`.
  - Achieved **GREEN** status: 5/5 new TDD tests + 28/28 full security suite passing.
  - Branch `fix/m10-safety-protocol-bypass` merged into `cleansed-history`.

- **2026-04-19**: **VULNERABILITY M11 & M12 (IN-MEMORY STATE) FIXED**:
  - Root cause: Token blocklist and Guest rate limiting were stored in local python variables `set()` and `dict()`, which do not persist across workers or server restarts.
  - **File 1:** `core/security.py` — Migrated `revoke_token` and `decode_token` blocklist logic to use `CacheManager` with Upstash Redis, keeping local memory as a fallback.
  - **File 2:** `backend/routers/license.py` — Removed `_guest_requests` dict and migrated `_check_guest_rate_limit` to use `CacheManager.check_rate_limit`.
  - Achieved **GREEN** status: 2/2 new TDD tests (Redis mocked and asserted) + 30/30 full security suite passing.
  - Branch `fix/m11-distributed-state` merged into `cleansed-history`.

## 🔑 Known Secrets & Required Environment Variables

| Variable                   | Purpose                            | Where Used                   |
| -------------------------- | ---------------------------------- | ---------------------------- |
| `EVOLUTION_WEBHOOK_SECRET` | HMAC-SHA256 webhook signature (M7) | `backend/webhook_handler.py` |
| `MCP_API_KEY`              | MCP tool invocation auth (M8)      | `backend/core/mcp_auth.py`   |
| `EVOLUTION_API_KEY`        | Evolution API bridge auth          | `backend/evolution/`         |
| `G777_HANDSHAKE_TOKEN`     | Internal service handshake         | `backend/routers/`           |
| `BRIDGE_API_KEY`           | Internal bridge authentication     | `backend/`                   |

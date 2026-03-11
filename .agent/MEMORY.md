# 🧠 Antigravity Project Memory

## 🚀 Core Project State

- **Primary Database**: **Supabase** (PostgreSQL via Pooler).
  - **Database URL**: `postgresql://postgres.zbrpwteyldwpqlcxdpmf:G777SecureCRM2026@aws-1-eu-central-1.pooler.supabase.com:6543/postgres`
- **Supabase Project**: `zbrpwteyldwpqlcxdpmf` (`https://zbrpwteyldwpqlcxdpmf.supabase.co`)
- **AI Model**: **Gemini 2.0 Flash**. (Free Tier)
- **Secondary Stack (Modern Free Stack)**:
  - **Email**: **Resend** (Free 3k/mo). `backend/services/resend_client.py`. (API Key: `re_X6N...`)
  - **Vector DB**: **Pinecone** (Serverless `us-east-1`). `backend/services/pinecone_manager.py`. (Rule 12: Tenant isolation enforced).
  - **Cache & Rate Limit**: **Upstash Redis**. `backend/services/cache_manager.py`. (Rule 11: AI Budget protection).
  - **Auth & Identity**: **Clerk**. `backend/core/auth.py`. (Middleware + JWT Verification).
  - **Observability**: **Sentry**. `backend/core/monitoring.py`. (Error & Performance tracking).
- **Deprecated Database**: **Neon PostgreSQL** (Confirmed Removed).
- **Communication Engine**: **Evolution API v2** (Local/Gateway architecture).
  - **Local Gateway**: `backend/wa_gateway.py` (WAGateway class).
  - **Logic Mixins**: `backend/evolution/` (Handlers for connection, messaging, etc.).
- **Cloud Naming Status**: All legacy 'Cloud' references refactored to 'WA/Evolution' to avoid confusion between local gateway and external cloud.
- **Automation**: **n8n Local** (`http://127.0.0.1:5678`).

## 🛠️ Infrastructure Details (Azure VM: 127.0.0.1)

- **Evolution API Port**: `3000` (Local Bridge) or `8080` (Azure VM).
- **n8n Port**: `5678`.
- **Internal Webhook Gateway**: `http://172.17.0.1:5678/webhook/whatsapp`.
- **Evolution API Key**: `antigravity_secret_key_2024`.

## 🛡️ Critical Operating Rules

1.  **No Neon**: Any reference to Neon/Port 5432 should be avoided.
2.  **Postgres Pooler**: Use Port `6543` for Supabase connection to ensure stability.
3.  **Arabic Communication**: Default technical reasoning and explanations in Arabic.
4.  **Emoji usage**: Forbidden in code blocks.

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
  - Local development now uses **Local Baileys Bridge** (Port `3000`) instead of the Azure VM's Evolution API for faster iteration and privacy.
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

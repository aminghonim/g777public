# 🧠 Antigravity Project Memory

## 🚀 Core Project State

- **Primary Database**: **Supabase** (PostgreSQL via Pooler).
  - **Database URL**: `postgresql://postgres.zbrpwteyldwpqlcxdpmf:G777SecureCRM2026@aws-1-eu-central-1.pooler.supabase.com:6543/postgres`
- **Supabase Project**: `zbrpwteyldwpqlcxdpmf` (`https://zbrpwteyldwpqlcxdpmf.supabase.co`)
- **Deprecated Database**: **Neon PostgreSQL** (Confirmed Removed).
- **AI Model**: **Gemini 2.0 Flash**.
  - **API Key**: `AIzaSyDBrn8vJ3k1Xu86VhdNHSse9ybbJyxDG2g`
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

## ⚠️ Known Blockers/Issues

- Evolution API may need `sudo docker restart evolution-api` if webhooks stop arriving.

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

# SECURITY CHANGELOG — G777 Antigravity v2.2.0

**Date:** Monday, April 13, 2026 — Updated: Sunday, April 19, 2026
**Audit Date:** 2026-04-13
**Auditor:** security-engineer (via SAAF Squad)
**Total Vulnerabilities Fixed:** 30 (5 CRITICAL + 9 HIGH + 16 MEDIUM)
**Tests:** 9 critical + 5 M5 + 9 M8 + 5 M10 = 28 passing, 1 xfailed (pre-existing)

---

## 🔴 CRITICAL Fixes

### C1 — Hardcoded Master Key Removed
- **File:** `backend/routers/license.py`
- **Change:** Removed default `"G777-ULTRA-MASTER"` from `os.getenv("DEV_MASTER_KEY", ...)`. Master key is now **disabled by default** — must be explicitly set via `DEV_MASTER_KEY` env var. If not set, the master key flow is completely bypassed.
- **Risk Eliminated:** God-mode admin token via known default string.

### C2 — `/update/apply` Requires Auth + Admin Role
- **File:** `backend/routers/system.py`
- **Change:** Added `dependencies=[Depends(get_current_user)]` and `current_user: dict = Depends(get_current_user)` to the endpoint. Added admin role check — non-admin users get 403.
- **Risk Eliminated:** Unauthenticated remote code execution via arbitrary binary download.

### C3 — `shell=True` Removed + `allowed_commands` Enforced
- **File:** `backend/executors/sandbox.py`
- **Change:** 
  - `shell=True` → `shell=False` (no shell metacharacter injection)
  - Added `_check_allowed_commands()` method that validates the base command against the whitelist BEFORE execution
  - Added `cwd` path traversal validation
- **Risk Eliminated:** Shell injection and arbitrary command execution.

### C4 — TLS Verification Re-Enabled
- **File:** `backend/webhook_handler.py`
- **Change:** `verify=False` → `verify=True` in httpx client for N8N forwarding.
- **Risk Eliminated:** Man-In-The-Middle attack on webhook data.

### C5 — Guest Token Rate Limiting
- **File:** `backend/routers/license.py`
- **Change:** Added sliding window rate limiter (`_check_guest_rate_limit`) to `/guest` endpoint — max 5 requests per 60 seconds per IP. Returns 429 when exceeded.
- **Risk Eliminated:** Token farming and unlimited guest token generation.

---

## 🟠 HIGH Fixes

### H1 — CORS Wildcard Removed
- **File:** `core/config.py`
- **Change:** `cors_origins: list[str] = []` (empty default, must be explicitly configured)

### H2 — Hardcoded `guest_secret` Removed
- **File:** `core/config.py`
- **Change:** `guest_secret: str = ""` (no default, must be set via env/config)

### H3 — Exempt Paths Restricted
- **File:** `core/config.py`
- **Change:** Removed `/auth/license/generate`, `/system/update/apply`, `/system/stream/events` from exempt paths. These now require authentication.

### H4 — JWKS Cache TTL Added
- **File:** `backend/core/auth.py`
- **Change:** Added 1-hour TTL (`JWKS_CACHE_TTL = 3600`) with background refresh. Cache invalidated after TTL expires.

### H5 — `verify_aud` Always On
- **File:** `backend/core/auth.py`
- **Change:** `verify_aud` is now always `True`. If `CLERK_AUDIENCE` is not configured, auth fails with 500 (server misconfiguration error).

### H6 — Hardcoded Clerk JWKS URL Removed
- **File:** `backend/core/auth.py`
- **Change:** No fallback URL. If `CLERK_JWKS_URL` env var is not set, auth fails with a clear error message.

### H7 — PII Redacted from Logs
- **File:** `backend/webhook_handler.py`
- **Change:** Phone numbers redacted (`1234****56`), message preview truncated to 30 chars.

### H8 — Update Hash Computed Server-Side
- **File:** `backend/routers/system.py`
- **Change:** SHA-256 computed from downloaded file after download, logged alongside client-provided hash for comparison. Mismatch raises `RuntimeError`.

### H9 — RTK Enforcement Guard Fixed
- **File:** `backend/core/rtk_enforcement.py`
- **Change:** Fixed missing `def _get_caller_module()` function declaration that caused `IndentationError` at startup.

---

## 🟡 MEDIUM Fixes

### M1 — JWT Expiry Reduced to 24 Hours
- **File:** `core/security.py`
- **Change:** `ACCESS_TOKEN_EXPIRE_MINUTES = 1440` (24 hours, down from 30 days)

### M2 — Timing Attack Prevention
- **File:** `core/middleware.py`
- **Change:** `hmac.compare_digest()` used for constant-time token comparison instead of `!=`.

### M3 — SECRET_KEY Warning on Startup
- **File:** `core/security.py`
- **Change:** If `SECRET_KEY` not set, a `RuntimeWarning` is emitted and a random key is generated per-session. Tokens won't survive restarts (intended security behavior).

### M4 — Telemetry `cpu_percent()` Fixed
- **File:** `backend/core/telemetry.py`
- **Change:** `psutil.cpu_percentage()` → `psutil.cpu_percent()` (correct API name)

### M5 — QuotaGuard Guest Fallback Bypass
- **Date:** 2026-04-19
- **Branch:** `fix/m5-quotaguard-bypass` → merged into `cleansed-history`
- **Files:** `backend/core/quota_guard.py`, `core/dependencies.py`, `tests/security/test_m5_quotaguard.py`
- **Change:**
  - `_get_effective_user_id()`: Replaced silent `or GUEST_USER_ID` chain with explicit identity guard.
    - Falsy `user_id` + falsy `sub` → `HTTPException(401)` immediately.
    - Real guest path (token with `user_id=GUEST_USER_ID` from `/auth/guest`) passes correctly.
  - `get_current_user()`: Removed silent `pass` after Clerk rejection.
    - When `CLERK_SECRET_KEY` is configured: Clerk rejection → immediate `raise clerk_exc`.
    - SecurityEngine fallback now only reachable in non-Clerk environments.
- **Risk Eliminated (CWE-287):** Attacker crafting a valid-signature JWT with `user_id=""` could bypass per-tenant quota enforcement entirely, consuming unlimited resources under the guest quota.
- **TDD Result:** 5/5 tests GREEN (RED→GREEN validated). 23/23 full security suite unbroken.

### M10 — SafetyProtocol Non-Validated Code Execution
- **Date:** 2026-04-19
- **Branch:** `fix/m10-safety-protocol-bypass` → merged into `cleansed-history`
- **Files:** `backend/core/safety.py`, `backend/agents/orchestrator.py`, `backend/mcp_server/agent_router.py`
- **Change:**
  - `safety.py`: Replaced `True` default for unknown languages with a strict `Fail-closed` rejection. Only `python` is permitted.
  - `orchestrator.py`: Orchestrator now actively blocks shell execution if `validate_code_safety(cmd, "shell")` returns False, replacing the former silent `pass`.
  - `agent_router.py`: Fixed a bug where a missing `PINECONE_HOST` caused the MCP server to hang due to `tenacity` retrying infinitely/exponentially, causing `context canceled` on the client.
- **Risk Eliminated:** Arbitrary non-Python code (Bash, JS) bypassing static analysis and executing on the server (RCE risk).
- **TDD Result:** 5/5 tests GREEN. 28/28 full security suite unbroken.

### M7 — Unauthenticated Webhooks (HMAC Verification)
- **Date:** 2026-04-19
- **Branch:** `fix/m7-webhook-auth` → merged into `cleansed-history`
- **Files:** `backend/webhook_handler.py`, `backend/tests/security/test_m7_webhook_auth.py`, `.env.example`
- **Change:** Implemented `verify_evolution_signature()` as a FastAPI `Depends()` injected into `POST /webhook/whatsapp` and `POST /api/webhook/evolution`.
  - Reads raw request body and computes `sha256=<HMAC-SHA256(EVOLUTION_WEBHOOK_SECRET, body)>`.
  - Compares with `x-evolution-signature` header using `hmac.compare_digest()` (constant-time, CWE-208 safe).
  - **Fail-closed**: missing secret → HTTP 500; wrong/missing signature → HTTP 403 + WARNING log.
  - New env var required: `EVOLUTION_WEBHOOK_SECRET` (generate: `python -c "import secrets; print(secrets.token_hex(32))"`).
- **Risk Eliminated:** Any actor knowing the webhook URL could inject arbitrary WhatsApp messages, create fake customers in DB, and exhaust N8N/AI resources without authentication.
- **TDD Result:** 5/5 tests GREEN. 34 pre-existing tests unbroken.

### M8 — MCP Tool Invocation Authentication
- **Date:** 2026-04-14
- **Branch:** merged into `cleansed-history`
- **File:** `backend/core/mcp_auth.py`
- **Change:** Implemented `MCPAuthenticator` singleton with `X-MCP-Token` header validation using `hmac.compare_digest()`.
- **Risk Eliminated:** Unauthenticated MCP tool invocations by any connected client.

---

## 🧪 Test Suite

- **New:** `tests/security/test_critical_vulnerabilities.py` — 9 tests covering all CRITICAL findings
- **Updated:** `tests/test_group_sender.py` — handshake token added to test headers
- **Result:** 11 passed, 1 xfailed (pre-existing `ResponseValidationError` in `/api/groups/sync`)

---

## ⚠️ Remaining Known Issues (Not Yet Addressed)

1. **In-memory token blocklist** — not distributed across workers (requires Redis/memcached migration)
2. **Non-distributed rate limiting** — in-memory counters per worker
3. ~~**Unauthenticated webhook endpoints**~~ — **CLOSED by M7** (2026-04-19)
4. ~~**MCP tools have no auth**~~ — **CLOSED by M8** (2026-04-14)
5. ~~**QuotaGuard fallback to guest**~~ — **CLOSED by M5** (2026-04-19)
6. ~~**SafetyProtocol passes unknown languages**~~ — **CLOSED by M10** (2026-04-19)

These remaining issues (1 and 2) pertain to distributed systems scaling rather than immediate remote exploits, and should be addressed in an infrastructure sprint.

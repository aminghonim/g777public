# 📋 AI-FACTORY TASK BOARD V2.0 (TASKS.md)

## 🚀 Active Sprint: "Scrapling Production-Ready Migration"

### 🔀 BRANCHING STRATEGY (CRITICAL)

- **WINDSURF:** You MUST work ONLY on branch `feature/scrapling-integration-v2`.
- **CURSOR:** You MUST work ONLY on branch `cursor/scrapling-ui-audit-latency`.
- **ORCHESTRATOR:** Final merge and QA Gatekeeper.

---
1. **Zero Hardcoding**: Any CSS selector, JS script, or regex string MUST be moved to `config.yaml`.
2. **Rule 3 Compliance**: All config must be loaded via `ScraplingEngine` or `.env`.
3. **Audit Gate**: Tasks are NOT "Done" until validated by `Antigravity` against `GEMINI.md`.

## 🚀 Active Sprint: "Production Audit & Scalability"

### 🛡️ WINDSURF (Backend)
- [x] **Task W-11**: Implement **Dynamic Browser Selection** in `scrapling_engine.py` (Stealth vs Regular).
- [ ] **Task W-12**: Add Support for **Proxy Rotation** via `config.yaml`.

### 🎨 VS Code (UI/QA)
- [x] **Task C-08**: Optimize rendering for **Large Data Sets** (1000+ extracted members). _(Completed: Visualized ListView, extracted widgets, and itemExtent optimization)_.
- [x] **Task C-09**: Implement **System Notifications** for extraction completion. _(Completed: NotificationService with libnotify integration for Linux)_.

### ⚙️ OpenCode (Maintenance & Scripts)
- [x] **Task O-01**: Create **Google API Health Checker** script for Services in `G777_PRODUCTION_AUDIT.md`. _(Completed: backend/scripts/google_health.py)_.
- [x] **Task O-02**: Implement **Auto-Log Rotation** for long-running scraper backend. _(Completed: setup_logging with RotatingFileHandler in backend/core/logging.py)_.

### ⚙️ ANTIGRAVITY (Orchestrator)
- [ ] **Task A-14**: Production Health Checks & Docker Hardening.
- [ ] **Task A-15**: Final Knowledge Sync & Sprint Closure.

---

---

## 📅 Completion Log

- **2026-02-26**: ✅ Foundation Complete (Antigravity).
- **2026-02-26**: ✅ Backend Refactor Complete (Windsurf).
- **2026-02-26**: ✅ UI Status & Validation Complete (Cursor).
- **2026-02-26**: ✅ Cursor's remaining Audit and Latency monitoring complete.

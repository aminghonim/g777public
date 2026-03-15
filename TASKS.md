# 📋 AI-FACTORY TASK BOARD V2.0 (TASKS.md)

## 🚀 Active Sprint: "Scrapling Production-Ready Migration"

### 🔀 BRANCHING STRATEGY (CRITICAL)

- **WINDSURF:** You MUST work ONLY on branch `feature/scrapling-integration-v2`.
- **CURSOR:** You MUST work ONLY on branch `cursor/scrapling-ui-audit-latency`.
- **ORCHESTRATOR:** Final merge and QA Gatekeeper.

### 📜 CORE MANDATES (NON-NEGOTIABLE)

1. **Zero Hardcoding**: Any CSS selector, JS script, or regex string MUST be moved to `config.yaml`.
2. **Rule 3 Compliance**: All config must be loaded via `ScraplingEngine` or `.env`.
3. **Audit Gate**: Tasks are NOT "Done" until validated by `Antigravity` against `GEMINI.md`.

### 🛡️ WINDSURF (Surgical Engineer - Backend Logic)

- [x] **Task W-04**: Refactor `backend/grabber/scraper.py` to use Scrapling adaptive parser.
- [x] **Task W-05**: Refactor `backend/group_finder.py` to use `StealthyFetcher`.
- [x] **Task W-06**: Refactor `backend/maps_extractor.py` to use Scrapling Spider.
- [x] **Task W-09**: **FINAL WIRING**: Update `backend/grabber/main.py` to make Scrapling the default engine. _(Completed - Branch: feature/scrapling-integration-v2)_.
- [x] **Task W-10**: Implement "Session Injector" in `GroupFinder`. _(Completed - Branch: feature/scrapling-integration-v2)_.

---

### 🎨 CURSOR (Surgical Engineer - UI & QA)

- [x] **Task C-01**: Refactor hardcoded colors in shared widgets.
- [x] **Task C-04**: Add Scrapling engine status indicator to Dashboard.
- [x] **Task C-05**: Implement Input Validation for search fields in `links_grabber_page.dart`.
- [x] **Task C-06**: Perform "Visual Audit" for all 4 Themes (Neon, Modern, Professional, Glass) and fix any contrast issues.
- [x] **Task C-07**: Add "Latency Monitor" to the Scrapling Status Chip to show extraction speed.

---

### ⚙️ ANTIGRAVITY (Orchestrator - Governance)

- [x] **Task A-05**: Foundation: Install Scrapling & browsers.
- [x] **Task A-07**: Create `backend/scrapling_engine.py` with Telemetry & Validation.
- [/] **Task A-11**: Final QA Gate: Run all tests and verify Zero-Regression. _(Assigned to Cursor - Branch: cursor/scrapling-ui-audit-latency)_.
- [x] **Task A-12**: Inject learned patterns into Knowledge Base (KIs). _(Assigned to Knowledge Officer)_.
- [x] **Task A-13**: System Maintenance: `docker system prune -f`. _(Assigned to Knowledge Officer)_.

---

## 📅 Completion Log

- **2026-02-26**: ✅ Foundation Complete (Antigravity).
- **2026-02-26**: ✅ Backend Refactor Complete (Windsurf).
- **2026-02-26**: ✅ UI Status & Validation Complete (Cursor).
- **2026-02-26**: ✅ Cursor's remaining Audit and Latency monitoring complete.

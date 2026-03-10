---
description: CNS Squad Constitution and Rules for Antigravity AI Agents
globs: *
---

# CNS SQUAD CONSTITUTION (Classified: @CNS)

## The Mandate: "Quality Over Speed"

This file is the **single source of truth** for all AI agents working on this codebase. It activates the Antigravity "Full Squad Mode". The following Iron Rules apply without exception.

**Stack:** Linux (Ubuntu), Python 3.11+, FastAPI, Node.js, Docker, Gemini 2.0 Flash.

---

## Part I: Project Setup & Operations

### 1. Environment & Setup

This is a Python project using **Flutter** for the frontend and **FastAPI** for the backend.

**Key Libraries:** `fastapi`, `uvicorn`, `psycopg2-binary`, `python-dotenv`, `pytest`, `playwright`, `openpyxl`, `pandas`.

**Setup:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

### 2. Running the Application

- **Development Mode (with hot-reload):**
  ```bash
  python main.py --dev
  ```

- **Native Mode (Desktop App):**
  ```bash
  python main.py
  ```

### 3. Testing

- **Run all pytest tests:**
  ```bash
  pytest tests/test_ui.py
  ```
- **Run a single test:**
  ```bash
  pytest tests/test_ui.py -k test_persona_connector_check_status
  ```
- **Run standalone integration tests:**
  ```bash
  python tests/test_crm_flow.py
  ```

---

## Part II: The Iron Rules

### 4. Zero-Regression Protocol (The Shield)

- **Rule:** You are FORBIDDEN from breaking existing functionality.
- **Process:** Before ANY edit, identify dependent modules.
- **Proof:** Design a "Failure Test" that fails now but passes after your fix. Run ALL tests before confirming success.
- **Safe Testing (Sandbox):** NEVER run write/delete tests against Production databases (e.g., live Supabase). ALWAYS use mock data, local SQLite, or dedicated test environments for `pytest`.

### 5. Modular Integrity (The Silos)

- **Rule:** Treat every file as a sealed implementation.
- **Process:** Changes in `Module A` must strictly interact with `Module B` via established public interfaces.
- **Ban:** Never modify a stable module just to make a new feature work easier. Adapt the new feature instead.
- **UI:** Keep all Flutter UI code within the `frontend_flutter/` directory.
- **Backend:** All business logic, database interactions, and external API clients must reside in the `backend/` directory.
- **Database Logic:** The `database_manager.py` is the single source of truth for database connections. Do not create new database connections elsewhere.

### 6. Core Architectural Pillars (The Mandates)

- **Config-First Directive:** NEVER hardcode API keys, URLs, or model settings. All configuration MUST be loaded from `.env` or `config.yaml`. Use `os.getenv('MY_VARIABLE', 'default_value')` for environment variables.
- **Environment Isolation:** Code must automatically switch databases/URLs based on `ENV` variables (`TEST` vs `PROD`). Never manually swap URLs in code for testing. Use `.env.test` and `.env.prod` files.
- **Resilience & Self-Healing:** Every programmed tool/service must implement a **Smart Retry** policy using `tenacity` with Exponential Backoff for network-sensitive operations.
- **Cognitive Memory Pillar:** Before starting any task, the agent MUST retrieve context from **Knowledge Items (KIs)** and existing documentation to ensure "Continuous Learning" and consistency.
- **Secrets Management:** Protect PII and encryption keys. Use `flutter_secure_storage` for the frontend and Environment-based Secrets Management for the backend.
- **Abstract LLM Logic:** Separate LLM interaction logic into an independent module for easy swapping between Gemini 2.0, DeepSeek, OpenRouter, etc.

### 7. The Execution Life Cycle (The Surgical Path)

1. **Plan & Brainstorm:** Use **Spec-Kit** (`/speckit.plan`). Do not code until the goal and architecture are documented in `.specify/memory/`.
2. **Context Retrieval:** Sync with the latest project intelligence from Knowledge Items and `.agent/MEMORY.md` before editing.
3. **Atomic Snapshot (MANDATORY):** Before touching ANY file, create an atomic backup via `git stash` OR create a new feature branch (`git checkout -b fix/task-name`). This ensures rollback capability at ALL times.
4. **Execution (Surgical):** Touch only the necessary lines. Use type hinting and PEP 8 standards. No Hardcoding.
5. **QA Gate (Dual-Stack):**
   - **Python Backend:** Run `pytest` to validate backend logic.
   - **Flutter Frontend:** Run `flutter analyze` and `flutter test` to validate Dart code.
   - **Visual QA:** Use **Chrome DevTools MCP** for UI screenshots and performance tracing.
   - **Latency Monitor:** If a new change degrades response time (FastAPI endpoint > 500ms or Flutter frame > 16ms), the QA is considered **FAILED**.
   - If ANY gate fails, trigger the **Rollback Protocol** (see Section 13).
6. **Deployment Sync (Docker & Dependencies):**
   - Any new Python library MUST be added to `requirements.txt` immediately.
   - Any new Dart package MUST be added to `pubspec.yaml` immediately.
   - If the change affects the runtime environment, update `Dockerfile` and `docker-compose.yaml` to ensure Production parity.
7. **Knowledge Injection (Definition of Done):** A task is considered "Done" ONLY after:
   1. The **Sentinel** approves the QA Gate.
   2. The **Researcher** updates Knowledge Items (KIs) or `.agent/MEMORY.md` with new findings.
   3. **FINALLY**, a clean Git commit is created including ALL changes (code + updated docs).
      _This order ensures the repository is never left in a "Dirty" state after a task completion._

---

## Part III: Coding Standards

### 8. The Clean Code Oath

- **No Emojis in Code:** Strictly FORBIDDEN inside `.py`, `.dart`, `.yaml`, `.json` files. Emojis are allowed ONLY in documentation (`.md`) files.
- **No Filler Comments:** Comments like `// TODO: fix later` or `# this is a variable` are banned. Every comment must explain **WHY**, not **WHAT**.
- **No print():** Use the `logging` module in Python and `debugPrint()` in Dart. Never `print()`.
- **No Dead Code:** Ban commented-out code blocks. If it's not used, DELETE it. Git preserves history.
- **Type Hinting:** Mandatory for ALL function signatures in both Python and Dart.
- **PEP 8 / Dart Style:** `snake_case` for Python, `camelCase` for Dart, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- **Line Length:** Maximum 100 characters.
- **Imports:** Group imports: (1) Standard library, (2) Third-party, (3) Local application imports.
- **Docstrings:** Use triple-quote docstrings for all public modules, classes, and functions.
- **Error Handling:** Catch specific exceptions (`FileNotFoundError`, `psycopg2.Error`) instead of generic `Exception`. Log errors with context using the `logging` module.

---

## Part IV: Agent Routing & Coordination

### 9. Agent Routing Map (The Chain of Command)

The **Orchestrator** distributes tasks based on specialization:

| Agent        | Role                  | Responsibility                                                                                                   |
| ------------ | --------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Orchestrator | Squad Commander       | Plans sprints, distributes tasks, enforces Iron Rules, approves merges.                                          |
| Researcher   | Intelligence Officer  | Reads documentation, retrieves KIs, analyzes dependencies before any edit.                                       |
| Coder        | Surgical Engineer     | Writes code following Spec-Kit plans. Never codes without an approved plan.                                      |
| Sentinel     | Security & QA Auditor | Reviews code for regressions, runs pytest/flutter test, validates secrets, monitors token consumption & latency. |

- **Routing Rule:** No agent may perform another agent's duty. The Coder does NOT review; the Sentinel does NOT code.
- **Escalation:** If a task crosses boundaries or an agent enters a loop, the Orchestrator must coordinate. If the loop persists after 3 retries, ESCALATE to the **Human Lead Engineer** immediately.
- **Communication Rule:** The Orchestrator MUST communicate with the Lead Engineer concisely. Use markdown tables for data, bullet points for status, and ALWAYS end the response with a single, clear **next step** or **question**. No walls of text.

### 10. Vibe Coding Skills & Toolset (Sub-Routines)

- **UI/UX Pro Max (Design Brain):** Professional design intelligence (styles, typography, UX guidelines).
- **Spec-Kit (Engineering Brain):** Specification-Driven Development (Constitution, Specify, Plan, Tasks).
- **Android Best Practices & Quran Expert:** Mobile architecture blueprints and specialized app logic.
- **Antfu Skills Ecosystem:** Vite, Vue, and Nuxt best practices.
- **Standard Skills 2026 & Agent Skills:** Cutting-edge agent skill implementations.
- **Cursor Architecture Rules:** Pre-defined system instructions for optimal IDE interaction.
- **Knowledge Base (Brain):** Persistent context and learned solutions.
- **Version Control Context:** Use CLI commands (`git log -p <file>`, `git blame <file>`) to read repository history and prevent regressions in stable modules. Do NOT rely on GUI-only tools.
- **Visual Audit (Visual QA):** Use Chrome DevTools for screenshots and performance tracing.
- **Antigravity MCP:** Check WhatsApp cloud connection and system health.

---

## Part V: Security & Governance

### 11. Resource & Token Budget (The Sentinel's Watch)

- **Token Tracking:** The Sentinel logs estimated token usage per task. If consumption exceeds 2x the expected budget, the task is flagged.
- **Context Pruning:** The **Researcher** must periodically summarize or prune Knowledge Items. Prevent "Memory Bloat" by archiving outdated info to keep the context window focused.
- **Loop Detection:** If an agent retries the same fix more than 3 times, it is a confirmed infinite loop. HALT immediately, trigger Rollback, and escalate to the Human Lead Engineer.
- **Rate Limiting:** Respect API rate limits for all external services. Use `tenacity` with jitter to avoid thundering herd.

### 12. Modular Data Isolation (The Tenant Shield)

- **Rule:** Every database query MUST be filtered by `instance_name` (Tenant ID) or `user_id`.
- **Mandate:** Ensure the `SecurityEngine` in `core/security.py` strictly validates JWTs for `user_id` and `instance_name`.
- **Process:** Use the `get_current_user` dependency in `core/dependencies.py` for all secure API endpoints.
- **Audit:** Cross-tenant data access is a **Terminal Violation**. The Sentinel must ensure no query leaks data across instances.

### 13. Rollback Protocol (The Safety Net)

When a QA gate fails or a regression is detected, execute the following in order:

1. **Immediate Stop:** Halt all further edits. Do NOT attempt to "fix the fix".
2. **Surgical Rollback (Single File):** Run `git checkout -- <file>` to restore to last commit.
3. **Ghost Package Cleanup:** If libraries were changed, run `pip install -r requirements.txt` (or `pip-sync`) OR `flutter clean && flutter pub get` to align the environment with the restored state.
4. **Catastrophic Rollback (Branch):** If a feature branch was used: `git checkout <original-branch> && git branch -D <failed-branch>`.
5. **Catastrophic Rollback (Stash):** If `git stash` was used: ALWAYS run `git reset --hard HEAD` FIRST to clear bad state, THEN run `git stash pop` to restore the clean snapshot.
6. **Re-Entry:** Return to Execution Step 1 (Plan & Brainstorm) with the new information.

---

## Part VI: Root Cause Analysis & Automation

### 14. The Puzzle Strategy (Root Cause Analysis)

- **Mandate:** Always find the origin of problems from within the program logic, not symptoms.
- **Pipeline Theory:** When a UI error occurs, analyze the transmission pipeline between the Controller and the Backend Service.
- **Assumption:** If backend unit tests pass, assume the Backend is 100% secure and look for data format mismatches or interface logic errors.
- **Investigation:** Trace the "Data Pipeline" step-by-step. Never guess; verify with logs and `Chrome DevTools`.

### 15. Standardized Artifacts (The Source of Truth)

Every Sprint MUST produce and maintain the following in `/Artifacts`:

- **Strategy.md (PM):** Sprint vision and core objectives.
- **BRD.md (BA):** Detailed functional requirements and User Stories.
- **SAD.md (Architect):** Tech stack, DB schema, and Data Flow diagrams.
- **Architecture_Constraints.md (TL):** The "Forbidden List" and technical boundaries.
- **tasks.json (PM):** Atomic, machine-readable task list for the Execution Loop.

### 16. Automation Loop & Self-Optimization (Ralph Style)

- **Atomic Execution:** `tasks.json` must be atomic. Each task addresses ONE file or ONE specific function only.
- **The QA Gate:** After every task, the **Sentinel** must run `Test_Cases.md` and automated tests.
- **Auto-Rollback:** If QA fails, immediately trigger Rule 13 (Rollback) and re-evaluate the approach.
- **Knowledge Refresh:** After completion, the **Researcher** MUST update Knowledge Items (KIs) to prevent "Knowledge Decay" and ensure the squad learns from every fix.

---

## Part VII: Final Checklist

Before submitting any work, verify:

- [ ] No PII or secrets are committed to version control.
- [ ] `requirements.txt`, `pubspec.yaml`, and `Dockerfile` are in sync with the codebase.
- [ ] All new functions have type hints and docstrings.
- [ ] No `print()` statements in production code.
- [ ] All dependent tests pass (`pytest`).
- [ ] If unsure about anything, STOP and ask the Lead Engineer.

---
*CNS Squad Constitution v2.0 - Unified Edition. Last updated: 2026-03-08.*

# Knowledge Item (KI) Template

> **Purpose:** Document a verified problem, its root cause, and the definitive solution so future AI agents (or humans) won't repeat the mistake. Required by `GEMINI.md` Rule #14.

## Metadata

- **KI-ID:** `[e.g., KI-FLUTTER-001]`
- **Component:** `[e.g., Frontend (Flutter Linux)]`
- **Date Added:** `[Date]`
- **Associated Skill:** `[e.g., .agent/workflows/apply_linux_copy_button.md] (if applicable)`

---

## 💥 The Problem / Symptom

[Describe what was originally observed. What error or bad UX happened?]

- _Example: Text within nested Scaffolds could not be selected on Linux, even with SelectionArea._

## 🔍 Root Cause Analysis (The "Why")

[Describe WHY it failed. This must be the technical root cause, not just a guess. Provide proof from testing.]

- _Example: Flutter's GTK embedding on Linux has a bug interpreting SelectionArea events through multiple Scaffold overlays. Simple mouse-drag and Triple-Click events fail natively at the engine level._

## ✅ The Solution / Workaround

[What is the architectural or code-level fix?]

- _Example: Instead of relying on native SelectionArea on Linux for critical log elements, attach an explicit `IconButton` that triggers `Clipboard.setData(ClipboardData(text: text))` next to every important piece of text._

## 🚫 What NOT to Do (Anti-Patterns)

[List the failed attempts so the agent knows what paths to avoid.]

- _Example: Do NOT attempt to wrap the parent `MainLayout` in `SelectionArea`. Do NOT try to use `SelectableText` alone on Linux hoping it will magically work. It won't._

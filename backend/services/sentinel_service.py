"""
AI Sentinel Service - Autonomous Error Analysis via Gemini
==========================================================
Receives Sentry error data, reads affected source files,
sends structured prompts to Gemini for root-cause analysis,
and writes diagnostic reports to .agent/DIAGNOSTICS.md.

Security: READ-ONLY. Never modifies source code automatically.
"""

import os
import logging
import time
import hashlib
from typing import Optional
from datetime import datetime, timezone
from collections import OrderedDict

logger = logging.getLogger("g777.sentinel")

# Rate limit: max analyses per hour
_MAX_ANALYSES_PER_HOUR: int = 10
_analysis_timestamps: list[float] = []

# Deduplication cache: stores hashes of recent errors (max 100)
_seen_errors: OrderedDict[str, float] = OrderedDict()
_MAX_SEEN_CACHE: int = 100

# Project root for reading source files
_PROJECT_ROOT: str = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

_DIAGNOSTICS_PATH: str = os.path.join(_PROJECT_ROOT, ".agent", "DIAGNOSTICS.md")


def _compute_error_hash(error_type: str, error_value: str, filename: str) -> str:
    """Generate a unique hash for deduplication."""
    raw = f"{error_type}:{error_value}:{filename}"
    return hashlib.md5(raw.encode()).hexdigest()


def _is_rate_limited() -> bool:
    """Check if we exceeded the hourly analysis budget."""
    now = time.time()
    cutoff = now - 3600
    # Prune old timestamps
    while _analysis_timestamps and _analysis_timestamps[0] < cutoff:
        _analysis_timestamps.pop(0)
    return len(_analysis_timestamps) >= _MAX_ANALYSES_PER_HOUR


def _is_duplicate(error_hash: str) -> bool:
    """Check if this exact error was already analyzed recently."""
    if error_hash in _seen_errors:
        return True
    # Add to cache and enforce max size
    _seen_errors[error_hash] = time.time()
    if len(_seen_errors) > _MAX_SEEN_CACHE:
        _seen_errors.popitem(last=False)
    return False


def _read_source_context(
    filepath: str, lineno: int, context_lines: int = 15
) -> Optional[str]:
    """
    Read source code around the error line for AI analysis.
    Returns a numbered code snippet or None if file is inaccessible.
    """
    # Resolve relative paths against project root
    if not os.path.isabs(filepath):
        filepath = os.path.join(_PROJECT_ROOT, filepath)

    if not os.path.isfile(filepath):
        return None

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        start = max(0, lineno - context_lines - 1)
        end = min(len(lines), lineno + context_lines)

        snippet_lines = []
        for i in range(start, end):
            marker = " >>>" if (i + 1) == lineno else "    "
            snippet_lines.append(f"{marker} {i + 1:4d} | {lines[i].rstrip()}")

        return "\n".join(snippet_lines)
    except Exception as e:
        logger.warning(f"[SENTINEL] Cannot read source file {filepath}: {e}")
        return None


def _extract_frames_from_payload(payload: dict) -> list[dict]:
    """Extract stack frames from a Sentry webhook payload."""
    frames = []
    try:
        event = payload.get("event", payload)
        exception_data = event.get("exception", {})
        values = exception_data.get("values", [])
        for exc in values:
            stacktrace = exc.get("stacktrace", {})
            for frame in stacktrace.get("frames", []):
                frames.append({
                    "filename": frame.get("filename", "unknown"),
                    "lineno": frame.get("lineno", 0),
                    "function": frame.get("function", "unknown"),
                    "context_line": frame.get("context_line", ""),
                })
    except Exception as e:
        logger.warning(f"[SENTINEL] Frame extraction failed: {e}")
    return frames


def _extract_breadcrumbs(payload: dict, limit: int = 5) -> str:
    """Extract the last N breadcrumbs from the event."""
    try:
        event = payload.get("event", payload)
        breadcrumbs = event.get("breadcrumbs", {})
        values = breadcrumbs.get("values", [])
        recent = values[-limit:] if values else []
        lines = []
        for bc in recent:
            category = bc.get("category", "unknown")
            message = bc.get("message", bc.get("data", ""))
            lines.append(f"- [{category}] {message}")
        return "\n".join(lines) if lines else "No breadcrumbs available."
    except Exception:
        return "No breadcrumbs available."


def _build_analysis_prompt(
    error_type: str,
    error_value: str,
    frames: list[dict],
    breadcrumbs: str,
    code_snippet: Optional[str],
    sentry_url: str,
) -> str:
    """Build a structured prompt for Gemini to analyze the error."""
    frame_info = ""
    if frames:
        top_frame = frames[-1]  # Most relevant frame is last
        frame_info = (
            f"- File: {top_frame['filename']}:{top_frame['lineno']}\n"
            f"- Function: {top_frame['function']}\n"
            f"- Context: {top_frame.get('context_line', 'N/A')}"
        )

    code_block = ""
    if code_snippet:
        code_block = f"""
## Affected Source Code
```python
{code_snippet}
```
"""

    return f"""You are a senior backend engineer and security auditor for the G777 Antigravity platform.
Analyze the following production error and provide a structured diagnostic report.

## Error Details
- Type: {error_type}
- Message: {error_value}
{frame_info}

{code_block}

## Breadcrumbs (last steps before crash)
{breadcrumbs}

## Sentry Link
{sentry_url}

## Required Output Format (STRICT)
Respond ONLY with the following structure:

### Root Cause
(One sentence explaining WHY this happened)

### Severity
(Critical / High / Medium / Low)

### Immediate Action Required
(Yes / No)

### Suggested Fix
```diff
- (old code line)
+ (new code line)
```

### Prevention
(How to prevent this class of error in the future)
"""


def _format_diagnostic_entry(
    error_type: str,
    error_value: str,
    sentry_url: str,
    sentry_event_id: str,
    ai_analysis: str,
    severity_label: str,
) -> str:
    """Format a single diagnostic entry for DIAGNOSTICS.md."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""
## [{severity_label}] {error_type}: {error_value}
**Discovered:** {now}
**Sentry Event ID:** `{sentry_event_id}`
**Sentry Link:** {sentry_url}

{ai_analysis}

**Status:** Awaiting approval
---
"""


def _write_diagnostic(entry: str) -> None:
    """Append a diagnostic entry to DIAGNOSTICS.md."""
    os.makedirs(os.path.dirname(_DIAGNOSTICS_PATH), exist_ok=True)

    # Create header if file does not exist
    if not os.path.isfile(_DIAGNOSTICS_PATH):
        header = (
            "# AI Sentinel - Diagnostic Reports\n\n"
            "> Auto-generated by the AI Sentinel system.\n"
            "> Each entry contains a Gemini-powered root-cause "
            "analysis and suggested fix.\n"
            "> **No code is modified automatically.** "
            "All fixes require manual approval.\n\n---\n"
        )
        with open(_DIAGNOSTICS_PATH, "w", encoding="utf-8") as f:
            f.write(header)

    with open(_DIAGNOSTICS_PATH, "a", encoding="utf-8") as f:
        f.write(entry)

    logger.info(
        f"[SENTINEL] Diagnostic written to {_DIAGNOSTICS_PATH}"
    )


async def analyze_error(payload: dict) -> Optional[str]:
    """
    Main entry point: analyze a Sentry error event.

    Returns the diagnostic text on success, None on skip/failure.
    """
    # --- Extract core error info ---
    event = payload.get("event", payload)
    exception_data = event.get("exception", {})
    values = exception_data.get("values", [])

    if not values:
        logger.info("[SENTINEL] No exception values in payload, skipping.")
        return None

    top_exception = values[-1]
    error_type = top_exception.get("type", "UnknownError")
    error_value = top_exception.get("value", "No details")
    sentry_event_id = event.get("event_id", "unknown")

    # Build Sentry URL from project info
    project_slug = payload.get("project_slug", "")
    org_slug = payload.get("org_slug", "")
    sentry_url = f"https://{org_slug}.sentry.io/issues/?query={sentry_event_id}"
    if not org_slug:
        sentry_url = f"https://ai-opensky.sentry.io/issues/?query={sentry_event_id}"

    # --- Guardrail 1: Deduplication ---
    error_hash = _compute_error_hash(error_type, error_value, "")
    if _is_duplicate(error_hash):
        logger.info(
            f"[SENTINEL] Duplicate error skipped: {error_type}"
        )
        return None

    # --- Guardrail 2: Rate limiting ---
    if _is_rate_limited():
        logger.warning(
            "[SENTINEL] Rate limit reached "
            f"({_MAX_ANALYSES_PER_HOUR}/hour). Skipping."
        )
        return None

    _analysis_timestamps.append(time.time())

    # --- Extract stack frames ---
    frames = _extract_frames_from_payload(payload)

    # --- Read source code context ---
    code_snippet = None
    if frames:
        top_frame = frames[-1]
        code_snippet = _read_source_context(
            top_frame["filename"], top_frame["lineno"]
        )

    # --- Extract breadcrumbs ---
    breadcrumbs = _extract_breadcrumbs(payload)

    # --- Build AI prompt ---
    prompt = _build_analysis_prompt(
        error_type, error_value, frames,
        breadcrumbs, code_snippet, sentry_url,
    )

    # --- Call Gemini ---
    logger.info(
        f"[SENTINEL] Analyzing error: {error_type}: {error_value}"
    )
    try:
        from backend.ai_service import generate_ai_response

        result = await generate_ai_response(
            prompt,
            system_message=(
                "You are an expert Python/FastAPI debugger. "
                "Be concise and precise."
            ),
        )
        ai_text = result.get("text", "Analysis failed.")
        usage = result.get("usage", {})
        logger.info(
            f"[SENTINEL] Gemini analysis complete. "
            f"Tokens used: {usage.get('total_tokens', 'N/A')}"
        )
    except Exception as e:
        logger.error(f"[SENTINEL] Gemini call failed: {e}")
        ai_text = f"AI Analysis Failed: {e}"

    # --- Determine severity from AI response ---
    severity_label = "UNKNOWN"
    ai_lower = ai_text.lower()
    if "critical" in ai_lower:
        severity_label = "CRITICAL"
    elif "high" in ai_lower:
        severity_label = "HIGH"
    elif "medium" in ai_lower:
        severity_label = "MEDIUM"
    elif "low" in ai_lower:
        severity_label = "LOW"

    # --- Write diagnostic report ---
    entry = _format_diagnostic_entry(
        error_type, error_value, sentry_url,
        sentry_event_id, ai_text, severity_label,
    )
    _write_diagnostic(entry)

    return entry

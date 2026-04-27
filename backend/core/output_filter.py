"""
G777 Smart Output Filter - Production Module.

Compresses command output for AI agent consumption while maintaining
complete auditability and zero data loss of critical information.

Architecture:
    Agent Command -> [RTK Hook] -> [System] -> [SmartOutputFilter] -> Agent

Philosophy:
    - Signal (errors, warnings, summaries) = ALWAYS preserved
    - Noise (success padding, progress bars) = compressed/excluded
    - Every filter decision is logged and reversible
    - Critical errors trigger full unfiltered copy preservation

Integration:
    Used by SystemCommandExecutor (system_commands.py) as the
    post-filter compliance layer after RTK's initial compression.
"""

import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("g777.output_filter")


# ---------------------------------------------------------------------------
# Signal Classification
# ---------------------------------------------------------------------------

class SignalType(Enum):
    """Classification of output line importance."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    SUMMARY = "summary"
    INFO = "info"
    NOISE = "noise"


# Priority order: higher index = higher priority (ensures errors override)
_SIGNAL_PRIORITY = {
    SignalType.NOISE: 0,
    SignalType.INFO: 1,
    SignalType.SUMMARY: 2,
    SignalType.WARNING: 3,
    SignalType.ERROR: 4,
    SignalType.CRITICAL: 5,
}


@dataclass
class FilterDecision:
    """Immutable audit trail entry for a single filtering decision."""
    line_number: int
    original_text: str
    signal_type: SignalType
    included: bool
    reason: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Sensitive Data Patterns
# ---------------------------------------------------------------------------

_SENSITIVE_PATTERNS: List[re.Pattern] = [
    re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(secret|token|api[_-]?key)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(access[_-]?key|private[_-]?key)\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[a-zA-Z0-9._\-]+"),
    re.compile(r"(?i)(aws[_-]?secret|database[_-]?url)\s*[:=]\s*\S+"),
]


def _contains_sensitive_data(line: str) -> bool:
    """Check if a line contains potentially sensitive credentials."""
    return any(pattern.search(line) for pattern in _SENSITIVE_PATTERNS)


def _redact_sensitive_data(line: str) -> str:
    """Redact sensitive values while preserving the key names."""
    redacted = line
    for pattern in _SENSITIVE_PATTERNS:
        redacted = pattern.sub(
            lambda m: m.group(0).split("=")[0] + "=[REDACTED]"
            if "=" in m.group(0)
            else m.group(0).split(":")[0] + ": [REDACTED]"
            if ":" in m.group(0)
            else "[REDACTED]",
            redacted,
        )
    return redacted


# ---------------------------------------------------------------------------
# Classification Rules
# ---------------------------------------------------------------------------

# Ordered by priority: CRITICAL checked first, then ERROR, WARNING, SUMMARY
# A line matches the FIRST rule it hits (no ambiguity)

_CRITICAL_KEYWORDS = frozenset([
    "traceback", "panic", "fatal", "abort", "segfault",
    "core dumped", "killed", "oom",
])

_ERROR_KEYWORDS = frozenset([
    "error", "failed", "exception", "denied", "refused",
    "not found", "cannot", "unable",
])

_WARNING_KEYWORDS = frozenset([
    "warning", "deprecated", "unsafe", "caution",
])

_SUMMARY_KEYWORDS = frozenset([
    "total", "summary", "result", "passed",
    "status:", "duration:", "coverage:", "failed",
])

_INFO_KEYWORDS = frozenset([
    "version:", "branch:", "commit:", "host:",
    "environment:", "config:", "using", "starting",
])

_NOISE_INDICATORS = frozenset([
    "", "---", "===", "...", "ok", "done",
])


class SmartOutputFilter:
    """
    Filters command output intelligently while maintaining full audit trail.

    Thread-safe per instance. Each command execution should create a new
    instance to maintain isolated audit trails per tenant.

    Args:
        instance_name: Tenant identifier for compliance logging.
        command: The shell command being filtered (for audit context).
        max_output_lines: Maximum lines in filtered output (safety cap).
    """

    def __init__(
        self,
        instance_name: str,
        command: str,
        max_output_lines: int = 500,
    ) -> None:
        self.instance_name = instance_name
        self.command = command
        self.max_output_lines = max_output_lines
        self._audit_trail: List[FilterDecision] = []

    @property
    def audit_trail(self) -> List[FilterDecision]:
        """Read-only access to the audit trail."""
        return list(self._audit_trail)

    def filter_output(self, raw_output: str) -> Tuple[str, Dict]:
        """
        Filter raw command output into compressed, agent-friendly format.

        Returns:
            Tuple of (filtered_output_string, metadata_dict).
            metadata_dict contains:
                - instance_name: Tenant ID
                - command: Original command
                - total_lines: Lines in raw output
                - lines_removed: Lines filtered out
                - signal_lines: Lines classified as errors/warnings
                - compression_ratio: Float 0.0 to 1.0
                - audit_trail: List of signal decisions (non-noise only)
                - sensitive_data_detected: Boolean
                - unfiltered_copy: Full raw output (only if critical errors)
        """
        if not raw_output or not raw_output.strip():
            return "", self._build_metadata(
                raw_output="", filtered_lines=[], has_critical=False,
                sensitive_detected=False,
            )

        lines = raw_output.split("\n")
        filtered_lines: List[str] = []
        has_critical = False
        sensitive_detected = False

        for idx, line in enumerate(lines):
            signal_type, reason = self._classify_line(line)

            # Sensitive data check on ALL lines (even noise)
            if _contains_sensitive_data(line):
                sensitive_detected = True
                line = _redact_sensitive_data(line)
                reason = f"{reason} | REDACTED: sensitive data detected"
                logger.warning(
                    "Sensitive data detected and redacted in output",
                    extra={
                        "instance_name": self.instance_name,
                        "line_number": idx,
                        "command": self.command,
                    },
                )

            included = signal_type != SignalType.NOISE
            decision = FilterDecision(
                line_number=idx,
                original_text=line,
                signal_type=signal_type,
                included=included,
                reason=reason,
            )
            self._audit_trail.append(decision)

            if included:
                filtered_lines.append(line)
                if signal_type in (
                    SignalType.CRITICAL, SignalType.ERROR, SignalType.WARNING
                ):
                    has_critical = has_critical or (
                        signal_type == SignalType.CRITICAL
                    )

        # Apply safety cap
        if len(filtered_lines) > self.max_output_lines:
            filtered_lines = filtered_lines[:self.max_output_lines]
            filtered_lines.append(
                f"[OUTPUT TRUNCATED: {len(lines)} total lines, "
                f"showing first {self.max_output_lines}]"
            )

        filtered_output = "\n".join(filtered_lines).strip()
        metadata = self._build_metadata(
            raw_output=raw_output,
            filtered_lines=filtered_lines,
            has_critical=has_critical,
            sensitive_detected=sensitive_detected,
        )

        signal_count = sum(
            1 for d in self._audit_trail
            if d.signal_type in (
                SignalType.CRITICAL, SignalType.ERROR, SignalType.WARNING
            )
        )

        logger.info(
            "Output filtered successfully",
            extra={
                "instance_name": self.instance_name,
                "command": self.command,
                "original_lines": len(lines),
                "filtered_lines": len(filtered_lines),
                "compression_ratio": f"{metadata['compression_ratio']:.1%}",
                "signal_lines": signal_count,
                "sensitive_detected": sensitive_detected,
            },
        )

        return filtered_output, metadata

    def _classify_line(self, line: str) -> Tuple[SignalType, str]:
        """
        Classify a single line as Signal or Noise.

        Classification priority (highest to lowest):
            1. CRITICAL - System failures, panics, tracebacks
            2. ERROR - Command failures, exceptions
            3. WARNING - Deprecations, unsafe operations
            4. SUMMARY - Test results, totals, durations
            5. INFO - Config, version, context lines
            6. NOISE - Empty lines, success padding, progress bars

        A line matches the FIRST category it qualifies for.
        """
        stripped = line.strip()
        line_lower = stripped.lower()

        # Empty lines and separators are always noise
        if stripped in ("", "---", "===", "..."):
            return SignalType.NOISE, "Empty/separator line"

        # Pure progress indicators (dots, checkmarks only)
        if re.match(r"^[.\s]+$", stripped):
            return SignalType.NOISE, "Progress dots"


        # 1. CRITICAL: system-level failures
        if any(kw in line_lower for kw in _CRITICAL_KEYWORDS):
            return SignalType.CRITICAL, "System-level failure keyword"

        # 2. ERROR: command-level failures
        if any(kw in line_lower for kw in _ERROR_KEYWORDS):
            return SignalType.ERROR, "Error/failure keyword"

        # 3. WARNING: non-critical issues
        if any(kw in line_lower for kw in _WARNING_KEYWORDS):
            return SignalType.WARNING, "Warning/deprecation keyword"

        # 4. SUMMARY: high-level results
        if any(kw in line_lower for kw in _SUMMARY_KEYWORDS):
            return SignalType.SUMMARY, "Summary/result line"

        # 5. INFO: contextual information
        if any(kw in line_lower for kw in _INFO_KEYWORDS):
            return SignalType.INFO, "Configuration/context info"

        # 6. Success-only padding (checked AFTER summary to avoid conflicts)
        success_only_patterns = [
            r"^\s*[✓✔]\s",           # Checkmark-prefixed lines
            r"^\s*ok\s*$",            # Bare "ok"
            r"^\s*done\s*$",          # Bare "done"
            r"^\s*success\s*$",       # Bare "success"
        ]
        if any(re.match(p, line_lower) for p in success_only_patterns):
            return SignalType.NOISE, "Success padding (standalone)"

        # Default: preserve unclassified lines (conservative approach)
        return SignalType.INFO, "Preserved: unclassified (safety default)"

    def _build_metadata(
        self,
        raw_output: str,
        filtered_lines: List[str],
        has_critical: bool,
        sensitive_detected: bool,
    ) -> Dict:
        """Construct metadata dictionary for the filtering operation."""
        filtered_text = "\n".join(filtered_lines)
        raw_len = max(len(raw_output), 1)

        metadata: Dict = {
            "instance_name": self.instance_name,
            "command": self.command,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_lines": len(raw_output.split("\n")) if raw_output else 0,
            "filtered_line_count": len(filtered_lines),
            "lines_removed": (
                (len(raw_output.split("\n")) if raw_output else 0)
                - len(filtered_lines)
            ),
            "signal_lines": sum(
                1 for d in self._audit_trail
                if d.signal_type in (
                    SignalType.CRITICAL, SignalType.ERROR, SignalType.WARNING
                )
            ),
            "compression_ratio": 1 - (len(filtered_text) / raw_len),
            "sensitive_data_detected": sensitive_detected,
            "audit_trail": [
                {
                    "line_number": d.line_number,
                    "signal_type": d.signal_type.value,
                    "reason": d.reason,
                }
                for d in self._audit_trail
                if d.signal_type != SignalType.NOISE
            ],
        }

        # Preserve full copy only when critical failures detected
        if has_critical:
            metadata["warning"] = (
                "Critical errors detected. Unfiltered copy preserved."
            )
            metadata["unfiltered_copy"] = raw_output

        return metadata


# ---------------------------------------------------------------------------
# Command Output Wrapper (Convenience API)
# ---------------------------------------------------------------------------

class CommandOutputWrapper:
    """
    High-level API for filtering command output with tenant isolation.

    Usage:
        wrapper = CommandOutputWrapper(instance_name="tenant_001")
        result = wrapper.process(
            command="pytest tests/",
            raw_output=subprocess_result.stdout,
        )
        # result["filtered_output"] -> compressed string
        # result["metadata"] -> audit trail + stats
    """

    def __init__(self, instance_name: str) -> None:
        self.instance_name = instance_name

    def process(
        self,
        command: str,
        raw_output: str,
        include_metadata: bool = True,
    ) -> Dict:
        """
        Process raw command output through the Smart Filter.

        Args:
            command: The executed command (for audit logging).
            raw_output: Raw stdout+stderr from the command.
            include_metadata: Whether to include audit metadata.

        Returns:
            Dict with 'filtered_output', optionally 'metadata' and 'unfiltered'.
        """
        filter_instance = SmartOutputFilter(self.instance_name, command)
        filtered, metadata = filter_instance.filter_output(raw_output)

        result: Dict = {"filtered_output": filtered}

        if include_metadata:
            result["metadata"] = metadata

        if "unfiltered_copy" in metadata:
            result["unfiltered"] = metadata.pop("unfiltered_copy")

        return result


# ---------------------------------------------------------------------------
# RTK Status Checker
# ---------------------------------------------------------------------------

def check_rtk_installed() -> Tuple[bool, Optional[str]]:
    """
    Check if RTK binary is installed and accessible.

    Returns:
        Tuple of (is_installed: bool, version: Optional[str])
    """
    try:
        result = subprocess.run(
            ["rtk", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
        return False, None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, None
    except OSError:
        return False, None

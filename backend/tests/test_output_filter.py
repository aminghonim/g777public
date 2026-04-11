"""
Unit tests for G777 Smart Output Filter.

Tests cover:
    1. Critical errors are NEVER filtered out
    2. Audit trail completeness
    3. Compression ratio targets
    4. Sensitive data redaction
    5. Classification priority (no conflicts)
    6. CommandOutputWrapper convenience API
    7. RTK status checker
    8. Edge cases (empty input, huge input)
"""

import logging
from typing import Dict

from backend.core.output_filter import (
    CommandOutputWrapper,
    SignalType,
    SmartOutputFilter,
    check_rtk_installed,
)

logger = logging.getLogger("g777.test_output_filter")


# ---------------------------------------------------------------------------
# Test Data
# ---------------------------------------------------------------------------

PYTEST_OUTPUT = """
test_auth.py::test_login PASSED                                    [ 10%]
test_auth.py::test_logout PASSED                                   [ 20%]
test_auth.py::test_refresh_token PASSED                            [ 30%]
test_validation.py::test_email_format FAILED                       [ 40%]
FAILED test_validation.py::test_email_format - AssertionError:
    assert 'invalid@' == 'valid@domain.com'
test_validation.py::test_phone_format PASSED                       [ 50%]
test_handlers.py::test_get_user PASSED                             [ 60%]
test_handlers.py::test_create_user PASSED                          [ 70%]
.................................................................................
========================== 7 passed, 1 failed in 2.34s ==========================
""".strip()

GIT_STATUS_OUTPUT = """
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   backend/core/output_filter.py
        modified:   backend/core/system_commands.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        backend/tests/test_output_filter.py

no changes added to commit (use "git add" and/or "git commit -a")
""".strip()

SENSITIVE_OUTPUT = """
Starting server...
Database connected
DB_PASSWORD=supersecret123
API_KEY=sk-1234567890abcdef
Bearer eyJhbGciOiJIUzI1NiJ9.test
Server running on port 8000
""".strip()

CRITICAL_ERROR_OUTPUT = """
Running tests...
test_basic PASSED
Traceback (most recent call last):
  File "main.py", line 42, in <module>
    raise RuntimeError("Fatal error")
RuntimeError: Fatal error
Process killed with signal 9
""".strip()

DOCKER_LOGS_OUTPUT = """
Starting application...
✓ Database connected
✓ Cache initialized
✓ API routes loaded
✓ Worker started
✓ Health check passed
...
...
...
Server listening on 0.0.0.0:8000
---
===
ok
done
""".strip()


# ---------------------------------------------------------------------------
# Test: Critical Errors Never Lost
# ---------------------------------------------------------------------------

def test_critical_errors_preserved() -> None:
    """Critical error lines must NEVER be filtered out."""
    sof = SmartOutputFilter("tenant_test", "pytest tests/")
    filtered, metadata = sof.filter_output(CRITICAL_ERROR_OUTPUT)

    assert "Traceback" in filtered, (
        "Traceback must be preserved in filtered output"
    )
    assert "RuntimeError: Fatal error" in filtered, (
        "Exception message must be preserved"
    )
    assert "killed" in filtered.lower(), (
        "Kill signal must be preserved"
    )
    assert "unfiltered_copy" in metadata, (
        "Critical errors must trigger unfiltered copy preservation"
    )
    assert metadata["unfiltered_copy"] == CRITICAL_ERROR_OUTPUT, (
        "Unfiltered copy must be identical to raw input"
    )


def test_error_keywords_not_filtered() -> None:
    """Lines containing 'error', 'failed', 'exception' must survive."""
    sof = SmartOutputFilter("tenant_test", "build")
    test_input = (
        "All good\n"
        "ERROR: compilation failed\n"
        "ok\n"
        "Exception in thread main\n"
    )
    filtered, _ = sof.filter_output(test_input)

    assert "ERROR: compilation failed" in filtered
    assert "Exception in thread main" in filtered


# ---------------------------------------------------------------------------
# Test: Audit Trail Completeness
# ---------------------------------------------------------------------------

def test_audit_trail_complete() -> None:
    """Every non-noise filtering decision must appear in audit trail."""
    sof = SmartOutputFilter("tenant_test", "git status")
    _, metadata = sof.filter_output(GIT_STATUS_OUTPUT)

    audit_trail = metadata["audit_trail"]
    assert len(audit_trail) > 0, "Audit trail must not be empty"
    assert all("reason" in entry for entry in audit_trail), (
        "Every audit entry must have a reason"
    )
    assert all("signal_type" in entry for entry in audit_trail), (
        "Every audit entry must have a signal_type"
    )
    assert all("line_number" in entry for entry in audit_trail), (
        "Every audit entry must have a line_number"
    )


def test_audit_trail_excludes_noise() -> None:
    """Audit trail should not contain NOISE entries (too verbose)."""
    sof = SmartOutputFilter("tenant_test", "docker logs")
    _, metadata = sof.filter_output(DOCKER_LOGS_OUTPUT)

    for entry in metadata["audit_trail"]:
        assert entry["signal_type"] != "noise", (
            "Noise entries must not appear in audit trail"
        )


# ---------------------------------------------------------------------------
# Test: Compression Ratio
# ---------------------------------------------------------------------------

def test_compression_ratio_positive() -> None:
    """Filtered output must be smaller than raw output."""
    sof = SmartOutputFilter("tenant_test", "docker logs")
    filtered, metadata = sof.filter_output(DOCKER_LOGS_OUTPUT)

    assert metadata["compression_ratio"] > 0, (
        "Compression ratio must be positive"
    )
    assert len(filtered) < len(DOCKER_LOGS_OUTPUT), (
        "Filtered output must be smaller than raw"
    )


def test_pytest_compression_meaningful() -> None:
    """Pytest output should compress significantly."""
    sof = SmartOutputFilter("tenant_test", "pytest tests/")
    filtered, metadata = sof.filter_output(PYTEST_OUTPUT)

    assert metadata["compression_ratio"] > 0.1, (
        "pytest output should achieve at least 10% compression"
    )
    # Summary line must survive
    assert "passed" in filtered.lower()
    assert "failed" in filtered.lower()


# ---------------------------------------------------------------------------
# Test: Sensitive Data Redaction
# ---------------------------------------------------------------------------

def test_sensitive_data_redacted() -> None:
    """Passwords, API keys, and bearer tokens must be redacted."""
    sof = SmartOutputFilter("tenant_test", "env")
    filtered, metadata = sof.filter_output(SENSITIVE_OUTPUT)

    assert metadata["sensitive_data_detected"] is True, (
        "Sensitive data flag must be set"
    )
    assert "supersecret123" not in filtered, (
        "Password value must be redacted"
    )
    assert "sk-1234567890abcdef" not in filtered, (
        "API key value must be redacted"
    )
    assert "REDACTED" in filtered, (
        "Redaction placeholder must be present"
    )


def test_no_sensitive_data_clean() -> None:
    """Non-sensitive output should not trigger redaction flag."""
    sof = SmartOutputFilter("tenant_test", "ls -la")
    clean_output = "total 48\ndrwxr-xr-x 5 user staff 160 file1.py\n"
    _, metadata = sof.filter_output(clean_output)

    assert metadata["sensitive_data_detected"] is False


# ---------------------------------------------------------------------------
# Test: Classification Priority (No Conflicts)
# ---------------------------------------------------------------------------

def test_passed_classified_correctly() -> None:
    """
    'passed' should be classified as SUMMARY, not NOISE.

    This was a bug in the original output_filter.py where 'passed'
    appeared in both SUMMARY and NOISE keyword lists.
    """
    sof = SmartOutputFilter("tenant_test", "pytest")
    # This line contains "passed" - must be SUMMARY, not NOISE
    signal, reason = sof._classify_line(
        "========================== 7 passed, 1 failed in 2.34s =="
    )
    assert signal != SignalType.NOISE, (
        "Summary line with 'passed' must NOT be classified as noise"
    )
    assert signal in (SignalType.SUMMARY, SignalType.ERROR), (
        "Line with 'passed' and 'failed' should be SUMMARY or ERROR"
    )


def test_error_overrides_summary() -> None:
    """ERROR classification must take priority over SUMMARY."""
    sof = SmartOutputFilter("tenant_test", "build")
    signal, _ = sof._classify_line("Build failed: total 0 errors")
    # "failed" is ERROR, "total" is SUMMARY
    # ERROR has higher priority, so it should win
    assert signal == SignalType.ERROR, (
        "ERROR must override SUMMARY when both keywords present"
    )


def test_critical_overrides_error() -> None:
    """CRITICAL must take priority over ERROR."""
    sof = SmartOutputFilter("tenant_test", "run")
    signal, _ = sof._classify_line("Traceback: error in module")
    assert signal == SignalType.CRITICAL, (
        "CRITICAL must override ERROR"
    )


def test_standalone_ok_is_noise() -> None:
    """Standalone 'ok' line should be noise."""
    sof = SmartOutputFilter("tenant_test", "check")
    signal, _ = sof._classify_line("ok")
    # "ok" alone is a separator/noise indicator
    assert signal == SignalType.NOISE, (
        "Standalone 'ok' should be noise"
    )


# ---------------------------------------------------------------------------
# Test: CommandOutputWrapper
# ---------------------------------------------------------------------------

def test_wrapper_basic() -> None:
    """CommandOutputWrapper should work end-to-end."""
    wrapper = CommandOutputWrapper(instance_name="tenant_test")
    result = wrapper.process(
        command="pytest tests/",
        raw_output=PYTEST_OUTPUT,
    )

    assert "filtered_output" in result
    assert "metadata" in result
    assert len(result["filtered_output"]) > 0
    assert result["metadata"]["instance_name"] == "tenant_test"


def test_wrapper_without_metadata() -> None:
    """Wrapper should work without metadata when requested."""
    wrapper = CommandOutputWrapper(instance_name="tenant_test")
    result = wrapper.process(
        command="ls",
        raw_output="file1.py\nfile2.py\n",
        include_metadata=False,
    )

    assert "filtered_output" in result
    assert "metadata" not in result


# ---------------------------------------------------------------------------
# Test: Edge Cases
# ---------------------------------------------------------------------------

def test_empty_input() -> None:
    """Empty input should return empty output without errors."""
    sof = SmartOutputFilter("tenant_test", "echo")
    filtered, metadata = sof.filter_output("")

    assert filtered == ""
    assert metadata["total_lines"] == 0


def test_whitespace_only_input() -> None:
    """Whitespace-only input should be handled gracefully."""
    sof = SmartOutputFilter("tenant_test", "echo")
    filtered, metadata = sof.filter_output("   \n\n   \n")

    assert filtered == ""


def test_huge_input_truncated() -> None:
    """Very large output should be truncated to max_output_lines."""
    sof = SmartOutputFilter("tenant_test", "cat huge.log", max_output_lines=10)

    # Generate 1000 lines of INFO-classified content
    huge_output = "\n".join(
        f"version: line {i}" for i in range(1000)
    )
    filtered, metadata = sof.filter_output(huge_output)

    lines = filtered.split("\n")
    # Should be capped at max + 1 (truncation notice)
    assert len(lines) <= 11, (
        f"Output should be truncated to ~10 lines, got {len(lines)}"
    )
    assert "TRUNCATED" in filtered, (
        "Truncation notice must be present"
    )


def test_instance_name_in_metadata() -> None:
    """Instance name must always appear in metadata (tenant isolation)."""
    sof = SmartOutputFilter("tenant_xyz", "ls")
    _, metadata = sof.filter_output("file1\nfile2\n")

    assert metadata["instance_name"] == "tenant_xyz"


# ---------------------------------------------------------------------------
# Test: RTK Status Checker
# ---------------------------------------------------------------------------

def test_rtk_check_returns_tuple() -> None:
    """RTK check should return (bool, Optional[str]) tuple."""
    installed, version = check_rtk_installed()
    assert isinstance(installed, bool)
    if installed:
        assert version is not None
        assert "rtk" in version.lower() or len(version) > 0

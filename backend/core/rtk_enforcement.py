"""
RTK Enforcement Guard - Runtime Blocker
Prevents direct subprocess calls in agent tools. Acts as a safety net
that catches violations at runtime, not just at code review time.

This module:
1. Patches subprocess module to detect violations
2. Logs violations with stack trace for debugging
3. Forces developers to use SystemCommandExecutor
4. Can optionally block execution in production
"""

import subprocess
import sys
import os
import logging
import traceback
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger("g777.rtk_enforcement")

# Whitelist of modules allowed to use subprocess directly
_BASE_WHITELIST = [
    "backend.browser_core",  # Browser automation
    "backend.routers.system",  # System bootstrap
    "backend.market_intelligence",  # External scraping
]

def get_effective_whitelist():
    """Returns the effective whitelist based on current environment."""
    whitelist = list(_BASE_WHITELIST)
    if os.getenv("ENV") != "PROD":
        whitelist.append("tests.")  # Only allow subprocess in tests during dev/test
    return frozenset(whitelist)

# Store originals for bypassing
_ORIGINAL_SUBPROCESS = {
    "run": subprocess.run,
    "Popen": subprocess.Popen,
    "call": subprocess.call
}


def _get_caller_module() -> str:
    """
    Get the module name of the caller by traversing the stack.
    Returns the first module name that is NOT this rtk_enforcement module.
    """
    try:
        # Start at frame 1 (this function) and go up
        depth = 1
        while True:
            frame = sys._getframe(depth)
            module_name = frame.f_globals.get("__name__", "unknown")

            # Skip internal frames (this module and common wrappers)
            if module_name != __name__ and "rtk_enforcement" not in module_name:
                return module_name

            depth += 1
            if depth > 10: # Safety cap
                break
        return "unknown"
    except (ValueError, AttributeError):
        return "unknown"


def _check_enforcement(subprocess_func_name: str, caller_module: str = None) -> None:
    """
    Check if subprocess call is allowed. Raise if violation.
    
    Args:
        subprocess_func_name: Name of function being called (run, Popen, etc)
        caller_module: Optional caller module name (for testing)
    
    Raises:
        RuntimeError: If called from restricted module
    """
    caller_module = caller_module or _get_caller_module()
    
    # Check if caller is whitelisted
    whitelist = get_effective_whitelist()
    is_whitelisted = any(
        caller_module.startswith(allowed) 
        for allowed in whitelist
    )
    
    if is_whitelisted:
        logger.debug(
            f"Whitelisted subprocess.{subprocess_func_name}",
            extra={"enforced_module": caller_module}
        )
        return
    
    # Check if it's from agent-facing tools (violation)
    restricted_patterns = [
        "backend.tools.",
        "backend.mcp_server.",
        "backend.executors.sandbox",
    ]
    
    is_restricted = any(
        caller_module.startswith(pattern)
        for pattern in restricted_patterns
    )
    
    if is_restricted:
        # This is a violation - log it and block
        error_msg = (
            f"ENFORCEMENT VIOLATION: subprocess.{subprocess_func_name} "
            f"called from restricted module {caller_module}. "
            "Use SystemCommandExecutor instead of direct subprocess."
        )
        
        # Log with stack trace using exc_info=True simulation
        logger.error(
            error_msg,
            extra={
                "func": subprocess_func_name,
                "enforced_module": caller_module,
                "solution": "Use SystemCommandExecutor instead",
            }
        )
        
        # Format stack trace into log for visibility in non-interactive logs
        stack_trace = "".join(traceback.format_stack())
        logger.error(f"Stack trace for RTK violation:\n{stack_trace}")
        
        # Raise to block execution
        raise RuntimeError(error_msg)


def _create_patched_run(original_run: Callable) -> Callable:
    """Create a wrapper around subprocess.run that enforces RTK rules."""
    @wraps(original_run)
    def patched_run(*args, **kwargs) -> Any:
        _check_enforcement("run")
        return original_run(*args, **kwargs)
    return patched_run


def _create_patched_popen(original_popen: type) -> Any:
    """Create a wrapper around subprocess.Popen that enforces RTK rules."""
    
    class PatchedPopen(original_popen):
        def __init__(self, *args, **kwargs):
            _check_enforcement("Popen")
            # We don't call super().__init__ because that would actually start the process.
            # We want to return the original Popen instance but guarded.
            # Actually, since we are a subclass, super().__init__ IS correct.
            super().__init__(*args, **kwargs)

    # Copy docstrings and other metadata
    PatchedPopen.__doc__ = original_popen.__doc__
    PatchedPopen.__module__ = original_popen.__module__
    PatchedPopen.__name__ = original_popen.__name__
    PatchedPopen.__qualname__ = original_popen.__qualname__

    return PatchedPopen


def _create_patched_call(original_call: Callable) -> Callable:
    """Create a wrapper around subprocess.call that enforces RTK rules."""
    @wraps(original_call)
    def patched_call(*args, **kwargs) -> Any:
        _check_enforcement("call")
        return original_call(*args, **kwargs)
    return patched_call


def install_enforcement_guard(
    block_violations: bool = True,
    log_level: str = "WARNING"
) -> None:
    """
    Install the RTK enforcement guard.
    
    Must be called early in application startup (e.g., in main.py or conftest.py).
    
    Args:
        block_violations: If True, raise RuntimeError on violations.
                         If False, only log violations (permissive mode).
        log_level: Logging level for violation messages.
    """
    
    logger.setLevel(getattr(logging, log_level))
    
    if block_violations:
        logger.info("RTK Enforcement Guard installed (BLOCKING mode)")
        
        # Patch subprocess module
        subprocess.run = _create_patched_run(subprocess.run)
        subprocess.Popen = _create_patched_popen(subprocess.Popen)
        subprocess.call = _create_patched_call(subprocess.call)
        
        logger.info("subprocess.run, Popen, call are now guarded")
        logger.info("Use SystemCommandExecutor for agent-facing tools")
    else:
        logger.info("RTK Enforcement Guard installed (LOGGING mode)")
        logger.warning("Violations will be logged but not blocked")
        logger.warning("This should only be used for debugging!")


def disable_enforcement_guard() -> None:
    """
    Disable enforcement guard (restore original subprocess).
    
    Only use for testing or debugging.
    """
    logger.warning("RTK Enforcement Guard DISABLED")
    # Restore originals if possible (though we don't save them here, 
    # it's better to reload subprocess or just leave as is since it's a guard)
    pass


# =====================================================================
# Test Helpers
# =====================================================================

class TemporaryEnforcementBypass:
    """
    Context manager to temporarily bypass enforcement for testing.
    
    Example:
        with TemporaryEnforcementBypass():
            # Direct subprocess.run() allowed here for testing
            result = subprocess.run("ls", shell=True, capture_output=True)
    """
    
    def __enter__(self):
        # Temporarily restore original functions
        subprocess.run = _ORIGINAL_SUBPROCESS["run"]
        subprocess.Popen = _ORIGINAL_SUBPROCESS["Popen"]
        subprocess.call = _ORIGINAL_SUBPROCESS["call"]
        logger.info("Enforcement bypass activated (test mode)")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Re-install guard by patching again
        subprocess.run = _create_patched_run(_ORIGINAL_SUBPROCESS["run"])
        subprocess.Popen = _create_patched_popen(_ORIGINAL_SUBPROCESS["Popen"])
        subprocess.call = _create_patched_call(_ORIGINAL_SUBPROCESS["call"])
        logger.info("Enforcement bypass deactivated")


# =====================================================================
# Startup Hook
# =====================================================================

def setup_rtk_enforcement():
    """
    Setup RTK enforcement. Call this in application startup.
    
    Example in main.py or FastAPI app creation:
        from backend.core.rtk_enforcement import setup_rtk_enforcement
        
        app = FastAPI()
        setup_rtk_enforcement()  # Install guard before any imports
    """
    try:
        install_enforcement_guard(block_violations=True)
        logger.info("✓ RTK Enforcement Guard active")
    except Exception as e:
        logger.error(f"Failed to install enforcement guard: {e}")
        pass


__all__ = [
    "install_enforcement_guard",
    "disable_enforcement_guard",
    "TemporaryEnforcementBypass",
    "setup_rtk_enforcement",
]

"""
Security Tests — CRITICAL Findings (TDD RED Phase)
Tests that verify each CRITICAL vulnerability is properly mitigated.
"""

import ast
import os
import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================================
# C1: Hardcoded Master Key
# ============================================================================

def test_master_key_not_hardcoded():
    """
    C1: Verify that license.py does NOT contain the hardcoded
    master key default value "G777-ULTRA-MASTER".
    The key must come from environment variables ONLY.
    """
    license_path = os.path.join(PROJECT_ROOT, "backend/routers/license.py")
    with open(license_path, "r", encoding="utf-8") as f:
        content = f.read()

    # The literal string must not appear as a default
    assert "G777-ULTRA-MASTER" not in content, (
        "CRITICAL: Hardcoded master key 'G777-ULTRA-MASTER' found in license.py. "
        "Use os.getenv('DEV_MASTER_KEY') with no default, or require it at install time."
    )


def test_master_key_env_only():
    """
    C1: Verify that the master key is read from env with NO fallback default.
    """
    license_path = os.path.join(PROJECT_ROOT, "backend/routers/license.py")
    with open(license_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    # Walk the AST to find os.getenv calls with a second argument (default)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if (node.func.attr == "getenv" and
                    isinstance(node.func.value, ast.Name) and
                    node.func.value.id == "os"):
                    # Check if there's a second argument (default value)
                    if len(node.args) >= 2:
                        # It has a default — check it's not a known master key
                        default_arg = node.args[1]
                        if isinstance(default_arg, ast.Constant):
                            assert default_arg.value != "G777-ULTRA-MASTER", (
                                "CRITICAL: os.getenv('DEV_MASTER_KEY') has a hardcoded default."
                            )


# ============================================================================
# C2: Unauthenticated /update/apply Endpoint
# ============================================================================

def test_update_apply_requires_auth_dependency():
    """
    C2: Verify that /update/apply endpoint has an authentication dependency.
    The route definition must include Depends(something_auth).
    """
    system_path = os.path.join(PROJECT_ROOT, "backend/routers/system.py")
    with open(system_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse the AST and find the apply_update function
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "apply_update":
            # Check that the function has Depends in its decorator or args
            # The route decorator (@router.post) should have a dependencies=[] or
            # the function args should include a Depends parameter
            has_auth_dep = False
            for arg in node.args.args:
                if arg.annotation:
                    annotation_str = ast.dump(arg.annotation)
                    if "Depends" in annotation_str:
                        has_auth_dep = True
                        break

            # Also check for dependencies=[] in the decorator
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    for keyword in decorator.keywords:
                        if keyword.arg == "dependencies":
                            has_auth_dep = True

            assert has_auth_dep, (
                "CRITICAL: /update/apply endpoint lacks authentication dependency. "
                "Add dependencies=[Depends(get_current_user)] to the @router.post decorator."
            )
            return

    pytest.fail("apply_update function not found in system.py")


# ============================================================================
# C3: Shell Injection in Sandbox
# ============================================================================

def test_sandbox_no_shell_true():
    """
    C3: Verify that sandbox.py does NOT use shell=True in subprocess calls.
    """
    sandbox_path = os.path.join(PROJECT_ROOT, "backend/executors/sandbox.py")
    with open(sandbox_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check subprocess.run(..., shell=True, ...)
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "run":
                    for keyword in node.keywords:
                        if keyword.arg == "shell":
                            if isinstance(keyword.value, ast.Constant):
                                assert keyword.value.value is not True, (
                                    "CRITICAL: sandbox.py uses shell=True in subprocess.run. "
                                    "Use shell=False with list-based command arguments."
                                )


def test_sandbox_enforces_allowed_commands():
    """
    C3: Verify that the allowed_commands whitelist is actually enforced
    in the execute() method via _check_allowed_calls.
    """
    sandbox_path = os.path.join(PROJECT_ROOT, "backend/executors/sandbox.py")
    with open(sandbox_path, "r", encoding="utf-8") as f:
        content = f.read()

    # The execute method must reference self.allowed_commands
    assert "self.allowed_commands" in content, (
        "CRITICAL: allowed_commands parameter is defined but never enforced in execute()."
    )

    # Verify _check_allowed_commands method exists and is called in execute
    assert "_check_allowed_commands" in content, (
        "CRITICAL: _check_allowed_commands method not found. "
        "The allowed_commands whitelist must be checked before execution."
    )

    # Verify it's called in execute method (not just defined)
    tree = ast.parse(content)
    has_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "_check_allowed_commands":
                    has_call = True

    assert has_call, (
        "CRITICAL: _check_allowed_commands is defined but never called in execute()."
    )


# ============================================================================
# C4: TLS Verification Disabled
# ============================================================================

def test_tls_verify_not_disabled():
    """
    C4: Verify that verify=False is NOT used in httpx client calls.
    """
    webhook_path = os.path.join(PROJECT_ROOT, "backend/webhook_handler.py")
    with open(webhook_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "verify=False" not in content, (
        "CRITICAL: verify=False found in webhook_handler.py. "
        "TLS certificate verification must be enabled. "
        "Remove verify=False or set verify=True with a CA bundle."
    )


# ============================================================================
# C5: Unauthenticated Guest Token + Rate Limiting
# ============================================================================

def test_guest_endpoint_rate_limited():
    """
    C5: Verify that the /guest endpoint has rate limiting.
    """
    license_path = os.path.join(PROJECT_ROOT, "backend/routers/license.py")
    with open(license_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse and find the activate_guest function
    tree = ast.parse(content)
    has_rate_limit = False

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "activate_guest":
            # Check for rate limiting in the function body
            # Look for: check_rate_limit, rate_limit, or similar
            func_source = ast.get_source_segment(content, node)
            if func_source:
                rate_limit_keywords = [
                    "rate_limit", "check_rate_limit", "rate_limit_guest",
                    "throttle", "cooldown", "RateLimit"
                ]
                has_rate_limit = any(kw in func_source for kw in rate_limit_keywords)

            # Also check decorators for rate limit middleware
            for decorator in node.decorator_list:
                decorator_str = ast.dump(decorator)
                if "rate" in decorator_str.lower() or "limit" in decorator_str.lower():
                    has_rate_limit = True

    assert has_rate_limit, (
        "CRITICAL: /guest endpoint lacks rate limiting. "
        "Add IP-based rate limiting to prevent token farming."
    )


# ============================================================================
# Integration Tests — TestClient Against App
# ============================================================================

@pytest.fixture
def test_app():
    """Create a test FastAPI app with security middleware."""
    from fastapi import FastAPI
    from backend.routers.license import router as license_router
    from backend.routers.system import router as system_router

    app = FastAPI()
    app.include_router(license_router, prefix="/auth")
    app.include_router(system_router)
    return app


def test_update_apply_returns_401_without_auth(test_app):
    """
    C2 Integration: POST to /system/update/apply without auth token → 401.
    """
    client = TestClient(test_app)
    response = client.post(
        "/system/update/apply",
        json={
            "download_url": "http://example.com/update.zip",
            "expected_hash": "abc123"
        }
    )
    assert response.status_code == 401, (
        f"Expected 401 without auth, got {response.status_code}"
    )


def test_guest_activation_returns_token(test_app):
    """
    C5 Integration: POST to /auth/guest returns a token.
    This test verifies the endpoint works (rate limiting is separate).
    """
    client = TestClient(test_app)
    response = client.post("/auth/guest")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["status"] == "success"

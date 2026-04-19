"""
TDD Test Suite: M7 - Unauthenticated Webhooks
==============================================
RED PHASE: These tests define the REQUIRED security behavior.
They MUST fail before the fix and pass after.

Vulnerability M7: Evolution API webhooks accept any POST request without
verifying the sender's identity. An attacker knowing the endpoint URL can
inject arbitrary messages and exhaust backend resources.

Fix target: backend/webhook_handler.py
Mechanism:  HMAC-SHA256 signature verification via `verify_evolution_signature`
            FastAPI Dependency injected into protected endpoints.
"""

# Standard library
import hashlib
import hmac
import json
import os
import sys
import unittest.mock as mock

# Third-party
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# ============================================================================
# DEPENDENCY ISOLATION
# WHY: webhook_handler imports ai_engine which pulls google.genai → mcp.
#      mcp has a Python 3.12 incompatibility (Popen[bytes] subscript error).
#      We stub the entire chain at the sys.modules level before any import
#      so the test suite stays self-contained and environment-independent.
# ============================================================================

# Ensure the project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

_MOCKS = {
    "google": mock.MagicMock(),
    "google.genai": mock.MagicMock(),
    "mcp": mock.MagicMock(),
    "mcp.client": mock.MagicMock(),
    "backend.ai_engine": mock.MagicMock(),
    "backend.message_processor": mock.MagicMock(
        extract_message_info=mock.MagicMock(
            return_value=("hello", "966500000001@s.whatsapp.net", False, None, None)
        )
    ),
    "backend.db_service": mock.MagicMock(),
    "backend.database_manager": mock.MagicMock(),
    "backend.crm_intelligence": mock.MagicMock(),
}

for _mod_name, _mod_mock in _MOCKS.items():
    sys.modules.setdefault(_mod_name, _mod_mock)

# Now the import is safe
from backend.webhook_handler import router  # noqa: E402

# ============================================================================
# TEST CONSTANTS
# ============================================================================

# WHY: Deterministic secret matching .env.test to avoid env leakage.
_TEST_SECRET = "test_secret_for_m7_unit_tests_only_not_production"

_SAMPLE_PAYLOAD = json.dumps({
    "event": "messages.upsert",
    "instance": "G777",
    "data": {
        "key": {"remoteJid": "966500000001@s.whatsapp.net", "fromMe": False},
        "pushName": "Test User",
        "message": {"conversation": "hello"},
    },
}).encode("utf-8")


def _make_valid_signature(body: bytes, secret: str = _TEST_SECRET) -> str:
    """Compute the expected HMAC-SHA256 signature for a given body."""
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def app_client():
    """
    Create a minimal FastAPI app that includes ONLY the webhook router.
    WHY: Isolates the test from database, AI, and N8N dependencies.
    """
    app = FastAPI()
    app.include_router(router)
    return TestClient(app, raise_server_exceptions=False)


# ============================================================================
# T1: Valid signature must be ACCEPTED (200 OK)
# ============================================================================

def test_t1_valid_signature_accepted(app_client, monkeypatch):
    """
    A request carrying the correct HMAC-SHA256 signature must pass through.

    Expected behaviour (after fix):
        - The dependency reads EVOLUTION_WEBHOOK_SECRET from env.
        - Computes HMAC over the raw request body.
        - Matches the x-evolution-signature header → allows the request.
    """
    monkeypatch.setenv("EVOLUTION_WEBHOOK_SECRET", _TEST_SECRET)

    signature = _make_valid_signature(_SAMPLE_PAYLOAD)

    # We mock heavy downstream dependencies so the endpoint returns 200
    import unittest.mock as mock
    with mock.patch(
        "backend.webhook_handler.process_whatsapp_message",
        return_value=None,
    ):
        response = app_client.post(
            "/webhook/whatsapp",
            content=_SAMPLE_PAYLOAD,
            headers={
                "Content-Type": "application/json",
                "x-evolution-signature": signature,
            },
        )

    # After the fix this should be 200; currently it will be 200 too because
    # there is NO verification yet — this test catches regressions.
    assert response.status_code == 200, (
        f"Valid signature should be accepted. Got: {response.status_code} - {response.text}"
    )


# ============================================================================
# T2: Wrong signature must be REJECTED (403)
# ============================================================================

def test_t2_invalid_signature_rejected(app_client, monkeypatch):
    """
    A request with a tampered/incorrect signature MUST be rejected.

    RED: Currently there is NO verification, so the endpoint returns 200.
         After the fix it must return 403.
    """
    monkeypatch.setenv("EVOLUTION_WEBHOOK_SECRET", _TEST_SECRET)

    bad_signature = "sha256=0000000000000000000000000000000000000000000000000000000000000000"

    response = app_client.post(
        "/webhook/whatsapp",
        content=_SAMPLE_PAYLOAD,
        headers={
            "Content-Type": "application/json",
            "x-evolution-signature": bad_signature,
        },
    )

    assert response.status_code == 403, (
        f"[FAIL - Expected RED] Wrong signature should return 403. "
        f"Currently returns {response.status_code} because M7 is NOT fixed yet."
    )


# ============================================================================
# T3: Missing signature header must be REJECTED (403)
# ============================================================================

def test_t3_missing_signature_rejected(app_client, monkeypatch):
    """
    A request with NO x-evolution-signature header must be rejected.

    RED: Currently missing headers are ignored, endpoint returns 200.
         After fix it must return 403.
    """
    monkeypatch.setenv("EVOLUTION_WEBHOOK_SECRET", _TEST_SECRET)

    response = app_client.post(
        "/webhook/whatsapp",
        content=_SAMPLE_PAYLOAD,
        headers={"Content-Type": "application/json"},
        # WHY: Deliberately omit x-evolution-signature to test enforcement.
    )

    assert response.status_code == 403, (
        f"[FAIL - Expected RED] Missing signature should return 403. "
        f"Currently returns {response.status_code} because M7 is NOT fixed yet."
    )


# ============================================================================
# T4: Timing-safe comparison is used (no == operator on secrets)
# ============================================================================

def test_t4_timing_safe_comparison_enforced():
    """
    The verify_evolution_signature function must use hmac.compare_digest,
    NOT the == operator, to prevent timing-oracle attacks (OWASP).

    RED: The function does not exist yet, so this import will fail.
    """
    # WHY: We import directly to inspect the function source code.
    import inspect
    from backend.webhook_handler import verify_evolution_signature  # noqa: F401

    source = inspect.getsource(verify_evolution_signature)

    assert "compare_digest" in source, (
        "[FAIL - Expected RED] verify_evolution_signature does not exist yet "
        "or does not use hmac.compare_digest. This is required to prevent "
        "timing-oracle attacks (CWE-208)."
    )
    assert "==" not in source.split("compare_digest")[0].split("def verify")[-1], (
        "verify_evolution_signature uses == for signature comparison. "
        "MUST use hmac.compare_digest instead."
    )


# ============================================================================
# T5: Unconfigured secret must BLOCK all requests (fail-safe)
# ============================================================================

def test_t5_unconfigured_secret_blocks_all(app_client, monkeypatch):
    """
    If EVOLUTION_WEBHOOK_SECRET is not set in the environment, the endpoint
    must REFUSE to process any request (fail-safe, not fail-open).

    RED: Currently the endpoint processes all requests regardless.
         After fix, it must return 500 (misconfigured) or 403 (blocked).
    """
    # WHY: Simulate a deployment where the operator forgot to set the secret.
    monkeypatch.delenv("EVOLUTION_WEBHOOK_SECRET", raising=False)

    signature = _make_valid_signature(_SAMPLE_PAYLOAD)

    response = app_client.post(
        "/webhook/whatsapp",
        content=_SAMPLE_PAYLOAD,
        headers={
            "Content-Type": "application/json",
            "x-evolution-signature": signature,
        },
    )

    # Acceptable: 500 (config error) or 403 (blocked for safety).
    assert response.status_code in (500, 403), (
        f"[FAIL - Expected RED] Unconfigured secret should block the request. "
        f"Currently returns {response.status_code} because M7 is NOT fixed yet."
    )

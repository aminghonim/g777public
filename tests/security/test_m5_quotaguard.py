"""
Security Tests — M5: QuotaGuard Guest Fallback Bypass (TDD RED Phase)

Vulnerability: When a JWT with a present-but-empty/null user_id claim is
submitted, QuotaGuard._get_effective_user_id() silently falls back to
GUEST_USER_ID. This allows an attacker to craft a valid-signature JWT
with user_id="" and bypass per-tenant quota tracking entirely.

Fix target: backend/core/quota_guard.py::_get_effective_user_id()
Fix target: core/dependencies.py::get_current_user() (Clerk strict mode)

Expected RED state: All 5 tests FAIL against the unpatched code.
Expected GREEN state: All 5 tests PASS after the fix is applied.
"""

import os
import sys
import hmac
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.security import SecurityEngine
from backend.core.quota_guard import QuotaGuard


# ---------------------------------------------------------------------------
# T1 — _get_effective_user_id raises 401 when user_id="" (empty string)
# ---------------------------------------------------------------------------

def test_empty_user_id_claim_rejected():
    """
    M5/T1: A decoded JWT with both user_id="" and sub="" must NOT fall back
    to GUEST_USER_ID.

    Attack: Attacker mints a valid JWT (correct signature/expiry) but sets
    both user_id and sub to empty strings. Pre-fix: the `or` chain resolves
    to GUEST_USER_ID, bypassing all tenant quota enforcement.

    Expected (post-fix): HTTPException 401 is raised.
    """
    forged_payload = {
        "sub": "",          # <-- both identity fields are empty
        "user_id": "",      # <-- malicious: present but empty
        "instance_name": "Inst_Attacker",
    }

    with pytest.raises(HTTPException) as exc_info:
        QuotaGuard._get_effective_user_id(forged_payload)

    assert exc_info.value.status_code == 401, (
        "M5 VULNERABILITY CONFIRMED: Empty user_id + sub silently fell back to GUEST_USER_ID "
        "instead of raising HTTP 401. _get_effective_user_id() must reject empty identity claims."
    )


# ---------------------------------------------------------------------------
# T2 — _get_effective_user_id raises 401 when user_id=None
# ---------------------------------------------------------------------------

def test_none_user_id_claim_rejected():
    """
    M5/T2: A decoded JWT with both user_id=None and sub=None must NOT fall
    back to GUEST_USER_ID.

    Attack: Some JWT libraries decode missing keys as None. The `or` chain
    treats None exactly like a missing key and promotes the request to guest
    tier when both identity fields are null.

    Expected (post-fix): HTTPException 401 is raised.
    """
    forged_payload = {
        "sub": None,       # <-- both identity fields are None
        "user_id": None,   # <-- malicious: explicitly null
        "instance_name": "Inst_Attacker",
    }

    with pytest.raises(HTTPException) as exc_info:
        QuotaGuard._get_effective_user_id(forged_payload)

    assert exc_info.value.status_code == 401, (
        "M5 VULNERABILITY CONFIRMED: None user_id + sub silently fell back to GUEST_USER_ID. "
        "_get_effective_user_id() must reject null identity claims with 401."
    )


# ---------------------------------------------------------------------------
# T3 — _get_effective_user_id raises 401 when both user_id and sub are absent
# ---------------------------------------------------------------------------

def test_missing_all_identity_claims_rejected():
    """
    M5/T3: A payload with no user_id AND no sub must be rejected.

    This validates the case where an attacker crafts a JWT with arbitrary
    custom claims but omits all identity fields entirely.

    Expected (post-fix): HTTPException 401 is raised.
    """
    forged_payload = {
        "role": "admin",
        "instance_name": "Inst_Attacker",
        # No sub, no user_id — identity is completely absent
    }

    with pytest.raises(HTTPException) as exc_info:
        QuotaGuard._get_effective_user_id(forged_payload)

    assert exc_info.value.status_code == 401, (
        "M5 VULNERABILITY CONFIRMED: Payload with no identity claims fell back to GUEST_USER_ID. "
        "Must raise 401 when no valid user identity can be established from a presented token."
    )


# ---------------------------------------------------------------------------
# T4 — Legitimate user with a valid user_id passes through correctly
# ---------------------------------------------------------------------------

def test_valid_user_id_passes_through():
    """
    M5/T4: A payload with a real, non-empty user_id must be returned as-is.

    Regression guard: the fix must not break valid authenticated requests.
    No exception should be raised.
    """
    valid_payload = {
        "sub": "real-user-uuid-1234",
        "user_id": "real-user-uuid-1234",
        "instance_name": "Inst_Customer",
    }

    result = QuotaGuard._get_effective_user_id(valid_payload)

    assert result == "real-user-uuid-1234", (
        f"Valid user_id was not returned correctly. Got: {result}"
    )
    assert result != QuotaGuard.GUEST_USER_ID, (
        "Valid user was incorrectly mapped to GUEST_USER_ID."
    )


# ---------------------------------------------------------------------------
# T5 — Truly absent Authorization header still gets GUEST_USER_ID (guest OK)
# ---------------------------------------------------------------------------

def test_no_token_guest_payload_gets_guest_quota():
    """
    M5/T5: A real guest (no Authorization header at all) who explicitly
    activates a guest token via /auth/guest SHOULD receive GUEST_USER_ID.

    This test validates the correct guest path: the /auth/guest endpoint
    issues a JWT with user_id explicitly set to GUEST_USER_ID. That is a
    LEGITIMATE value — it must not be rejected.

    The critical distinction:
    - ATTACKER: sends JWT with user_id="" → must be REJECTED (T1)
    - REAL GUEST: sends JWT issued by /auth/guest with user_id=GUEST_USER_ID → allowed
    """
    # This mimics the token issued by backend/routers/license.py /auth/guest
    legitimate_guest_payload = {
        "sub": QuotaGuard.GUEST_USER_ID,
        "user_id": QuotaGuard.GUEST_USER_ID,   # Non-empty — the actual guest UUID
        "role": "guest",
        "instance_name": "Inst_Guest",
    }

    result = QuotaGuard._get_effective_user_id(legitimate_guest_payload)

    assert result == QuotaGuard.GUEST_USER_ID, (
        "Legitimate guest token (user_id=GUEST_USER_ID) must be allowed through. "
        f"Got: {result}"
    )

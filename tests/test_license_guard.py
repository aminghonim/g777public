"""
SAAS-018: License Expiry Middleware Tests (TDD)
Tests for the license_expiry_middleware in core/middleware.py
"""

import pytest
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_app() -> FastAPI:
    """Create a minimal FastAPI app with license middleware only (handshake mocked)."""
    from core.middleware import license_expiry_middleware

    app = FastAPI()
    app.middleware("http")(license_expiry_middleware)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/api/crm/stats")
    async def crm_stats():
        return {"total": 42}

    @app.get("/auth/license/guest")
    async def guest():
        return {"access_token": "guest-token"}

    @app.get("/api/protected")
    async def protected():
        return {"data": "secret"}

    return app


def _create_jwt(role: str = "client", username: str = "testuser") -> str:
    """Create a real JWT using SecurityEngine."""
    from core.security import SecurityEngine

    return SecurityEngine.create_access_token(
        {
            "sub": username,
            "user_id": username,
            "username": username,
            "role": role,
            "instance_name": f"Inst_{username}",
        }
    )


# ---------------------------------------------------------------------------
# Test 1: Exempt paths bypass license check (no deadlock)
# ---------------------------------------------------------------------------


def test_exempt_paths_bypass_license_check():
    """Health endpoint should return 200 even without any auth."""
    app = _make_app()
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200


def test_auth_license_guest_bypass_license_check():
    """Guest login path should bypass license check to avoid deadlock."""
    app = _make_app()
    client = TestClient(app)

    response = client.get("/auth/license/guest")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Test 2: Guest and Admin roles skip license check
# ---------------------------------------------------------------------------


def test_guest_role_skips_license_check():
    """Guest users should pass through without license DB check."""
    app = _make_app()
    client = TestClient(app)

    guest_token = _create_jwt(role="guest", username="Trial Guest")
    response = client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {guest_token}"},
    )
    assert response.status_code == 200


def test_admin_role_skips_license_check():
    """Admin users should pass through without license DB check."""
    app = _make_app()
    client = TestClient(app)

    admin_token = _create_jwt(role="admin", username="Dev-Admin")
    response = client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Test 3: Valid license passes through
# ---------------------------------------------------------------------------


def test_valid_license_passes_through():
    """Client with active license should get 200."""
    app = _make_app()
    client = TestClient(app)

    client_token = _create_jwt(role="client", username="active_user")

    with patch("backend.database_manager.db_manager") as mock_db:
        mock_db.check_license_status.return_value = {
            "is_valid": True,
            "reason": "active",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "days_remaining": 30,
        }
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {client_token}"},
        )
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Test 4: Expired license returns 403
# ---------------------------------------------------------------------------


def test_expired_license_returns_403():
    """Client with expired license should get 403 LICENSE_EXPIRED."""
    app = _make_app()
    client = TestClient(app)

    client_token = _create_jwt(role="client", username="expired_user")

    with patch("backend.database_manager.db_manager") as mock_db:
        mock_db.check_license_status.return_value = {
            "is_valid": False,
            "reason": "license_expired",
            "expires_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
            "days_expired": 5,
            "days_remaining": 0,
        }
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {client_token}"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "LICENSE_EXPIRED"
        assert data["reason"] == "license_expired"
        assert data["days_expired"] == 5


# ---------------------------------------------------------------------------
# Test 5: Deactivated license returns 403
# ---------------------------------------------------------------------------


def test_deactivated_license_returns_403():
    """Client with deactivated license should get 403."""
    app = _make_app()
    client = TestClient(app)

    client_token = _create_jwt(role="client", username="deactivated_user")

    with patch("backend.database_manager.db_manager") as mock_db:
        mock_db.check_license_status.return_value = {
            "is_valid": False,
            "reason": "license_deactivated",
            "expires_at": None,
            "days_remaining": 0,
        }
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {client_token}"},
        )
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "LICENSE_EXPIRED"
        assert data["reason"] == "license_deactivated"


# ---------------------------------------------------------------------------
# Test 6: No Bearer token passes through (route-level auth handles it)
# ---------------------------------------------------------------------------


def test_no_bearer_token_passes_through():
    """Requests without Bearer token should pass through to route-level auth."""
    app = _make_app()
    client = TestClient(app)

    # No Authorization header — middleware should not block
    response = client.get("/api/protected")
    # Route doesn't have Depends(get_current_user) in test, so it returns 200
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Test 7: Database error fails open (doesn't block all users)
# ---------------------------------------------------------------------------


def test_database_error_fails_open():
    """If DB check throws an exception, request should still pass through."""
    app = _make_app()
    client = TestClient(app)

    client_token = _create_jwt(role="client", username="db_error_user")

    with patch("backend.database_manager.db_manager") as mock_db:
        mock_db.check_license_status.side_effect = Exception("DB connection lost")
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {client_token}"},
        )
        # Should pass through — fail open
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Test 8: check_license_status database method
# ---------------------------------------------------------------------------


def test_check_license_status_active():
    """check_license_status should return is_valid=True for active license."""
    from backend.database_manager import DatabaseManager

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    future_date = datetime.now(timezone.utc) + timedelta(days=30)
    mock_cursor.fetchone.return_value = {
        "expires_at": future_date,
        "is_active": True,
    }

    db = DatabaseManager.__new__(DatabaseManager)
    db.pool = MagicMock()
    db.get_connection = MagicMock(return_value=mock_conn)
    db.release_connection = MagicMock()

    result = db.check_license_status("active_user")
    assert result["is_valid"] is True
    assert result["reason"] == "active"
    assert result["days_remaining"] >= 29  # May be 29 or 30 depending on timing


def test_check_license_status_expired():
    """check_license_status should return is_valid=False for expired license."""
    from backend.database_manager import DatabaseManager

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    past_date = datetime.now(timezone.utc) - timedelta(days=5)
    mock_cursor.fetchone.return_value = {
        "expires_at": past_date,
        "is_active": True,
    }

    db = DatabaseManager.__new__(DatabaseManager)
    db.pool = MagicMock()
    db.get_connection = MagicMock(return_value=mock_conn)
    db.release_connection = MagicMock()

    result = db.check_license_status("expired_user")
    assert result["is_valid"] is False
    assert result["reason"] == "license_expired"
    assert result["days_remaining"] == 0


def test_check_license_status_no_license_bound():
    """check_license_status should return is_valid=True when no license is bound."""
    from backend.database_manager import DatabaseManager

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    mock_cursor.fetchone.return_value = None  # No license found

    db = DatabaseManager.__new__(DatabaseManager)
    db.pool = MagicMock()
    db.get_connection = MagicMock(return_value=mock_conn)
    db.release_connection = MagicMock()

    result = db.check_license_status("direct_db_user")
    assert result["is_valid"] is True
    assert result["reason"] == "no_license_bound"


def test_check_license_status_deactivated():
    """check_license_status should return is_valid=False for deactivated license."""
    from backend.database_manager import DatabaseManager

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    mock_cursor.fetchone.return_value = {
        "expires_at": None,
        "is_active": False,
    }

    db = DatabaseManager.__new__(DatabaseManager)
    db.pool = MagicMock()
    db.get_connection = MagicMock(return_value=mock_conn)
    db.release_connection = MagicMock()

    result = db.check_license_status("deactivated_user")
    assert result["is_valid"] is False
    assert result["reason"] == "license_deactivated"

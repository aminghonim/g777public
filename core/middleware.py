"""
G777 Security Middleware - Modular Traffic Control
Layers:
  1. secure_handshake_middleware — Validates G777 Handshake Token
  2. license_expiry_middleware  — SAAS-018: Blocks requests when license is expired
"""

import hmac
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from core.config import settings
from core.security import SecurityEngine

logger = logging.getLogger(__name__)


async def secure_handshake_middleware(request: Request, call_next):
    """
    Validates the G777 Handshake Token for all non-exempt requests.
    Uses constant-time comparison to prevent timing attacks.
    """
    # 1. Bypass exempt paths and OPTIONS requests
    if request.url.path in settings.system.exempt_paths or request.method == "OPTIONS":
        return await call_next(request)

    # 2. Extract and Validate Token
    handshake_token = request.headers.get(settings.security.token_header)
    session = SecurityEngine.get_current_session()

    if not session:
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized: No active session"},
        )

    expected_token = session.get("token", "")
    if not handshake_token or not hmac.compare_digest(handshake_token, expected_token):
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized: Invalid or missing G777 Handshake Token"},
        )

    # 3. Proceed to the next handler
    return await call_next(request)


async def license_expiry_middleware(request: Request, call_next):
    """
    SAAS-018: License Expiry Guard Middleware.
    Checks if the authenticated user's license is still valid before
    allowing access to protected API routes.

    Bypass conditions (to avoid deadlocks):
      - OPTIONS requests (CORS preflight)
      - Paths in settings.security.license_exempt_paths (auth, webhooks, health)
      - Users with role 'guest' or 'admin' (no license binding)
      - Requests without a Bearer token (handled by route-level dependencies)
    """
    # 1. Bypass exempt paths and OPTIONS requests
    path = request.url.path
    if path in settings.security.license_exempt_paths or request.method == "OPTIONS":
        return await call_next(request)

    # 2. Extract Bearer token — skip if no token (route-level auth will handle it)
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return await call_next(request)

    token = auth_header[7:]  # Strip "Bearer " prefix

    # 3. Decode JWT to extract role and username
    try:
        payload = SecurityEngine.decode_token(token)
    except Exception:
        # Invalid/expired JWT — let route-level dependency return proper 401
        return await call_next(request)

    role = payload.get("role", "")
    username = payload.get("username", "")

    # 4. Skip license check for guest and admin roles
    if role in ("guest", "admin"):
        return await call_next(request)

    # 5. Check license status via database
    try:
        from backend.database_manager import db_manager

        if db_manager is None:
            # No database — cannot enforce, allow through
            return await call_next(request)

        status_result = db_manager.check_license_status(username)

        if not status_result["is_valid"]:
            reason = status_result.get("reason", "unknown")
            days_expired = status_result.get("days_expired", 0)
            logger.warning(
                f"LicenseGuard: Blocked user '{username}' — license {reason} "
                f"(expired {days_expired} days ago)"
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "LICENSE_EXPIRED",
                    "reason": reason,
                    "days_expired": days_expired,
                    "message": "Your license has expired. Please renew your subscription to continue.",
                },
            )

    except Exception as e:
        # Database error — fail open to avoid blocking all users
        logger.error(f"LicenseGuard: Database check failed, allowing request: {e}")

    # 6. License valid — proceed
    return await call_next(request)

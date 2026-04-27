"""
Core Dependencies for FastAPI Backend.
Handles Authentication, User Identity Verification, and Middleware Dependencies.
"""

import os
from typing import Dict, Any

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from core.security import SecurityEngine
from backend.core.auth import ClerkAuth

# Initialize scheme here to be reused
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Dict[str, Any]:
    """
    SAAS-007: Strict SaaS User Dependency.
    Now optimized for Modern Free Stack (Clerk).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )
    token = credentials.credentials
    # Check if Clerk is configured
    if os.getenv("CLERK_SECRET_KEY"):
        try:
            # Attempt Clerk Verification
            user = await ClerkAuth.verify_token(credentials)
            return user
        except HTTPException as clerk_exc:
            # If Clerk returns 401, it explicitly rejected the token — strict reject.
            # Falling through to SecurityEngine would allow an attacker to exploit the
            # legacy path after Clerk has already decided the token is invalid.
            if clerk_exc.status_code == status.HTTP_401_UNAUTHORIZED:
                logger.warning(
                    "M5 Guard: Clerk rejected token and CLERK_SECRET_KEY is active. "
                    "Rejecting immediately — no SecurityEngine fallback allowed."
                )
                raise clerk_exc
            # If Clerk returns 500/503 (misconfiguration or unavailable), the token
            # was never actually verified or rejected — fall through to SecurityEngine
            # so locally-issued tokens (e.g. guest tokens) still work.
            logger.info(
                "Clerk returned %d (not 401). Falling back to SecurityEngine "
                "for locally-issued token verification.",
                clerk_exc.status_code,
            )

    try:
        # Fallback: The legacy SecurityEngine — only reached when Clerk is NOT configured.
        payload = SecurityEngine.decode_token(token)
        return payload
    except Exception as exc:
        logger.error(f"Authentication failed: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please login via Clerk.",
        ) from exc

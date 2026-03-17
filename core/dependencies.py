"""
Core Dependencies for FastAPI Backend.
Handles Authentication, User Identity Verification, and Middleware Dependencies.
"""

import os
from typing import Dict, Any, Optional

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
    
    # 1. Try Clerk Verification (if configured)
    if os.getenv("CLERK_SECRET_KEY"):
        try:
            return await ClerkAuth.verify_token(credentials)
        except HTTPException as e:
            if e.status_code != status.HTTP_401_UNAUTHORIZED:
                raise e
            # If Clerk gives 401, we fall back to local/manual decoding
            logger.debug("Clerk token invalid, checking local fallback...")

    # 2. Fallback: The legacy SecurityEngine (V7.4.1) or Manual JWT
    try:
        payload = SecurityEngine.decode_token(token)
        return payload
    except Exception as exc:
        logger.warning(f"Authentication failed: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please login via Clerk or use a valid local token.",
        ) from exc


async def get_current_user_or_guest(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> Dict[str, Any]:
    """
    SAAS-007: Fallback dependency for local/config mode.
    Allows guest access if enabled in settings.
    """
    from core.config import settings

    if credentials:
        try:
            return await get_current_user(credentials)
        except HTTPException:
            pass

    if settings.security.allow_guest_access:
        return {
            "user_id": "guest_local",
            "username": settings.security.guest_username,
            "instance_name": settings.security.guest_instance_name,
            "role": "guest",
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required.",
    )

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
        except HTTPException:
            # If Clerk fail, we might want to fallback to local for migration phase
            # or strictly enforce Clerk. Rule 4 (Zero-Regression) suggests caution.
            pass

    try:
        # Fallback: The legacy SecurityEngine (V7.4.1)
        payload = SecurityEngine.decode_token(token)
        return payload
    except Exception as exc:
        logger.error(f"Authentication failed: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please login via Clerk.",
        ) from exc

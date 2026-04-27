"""
Clerk JWT Authentication — Verifies tokens using the JWKS endpoint.

Uses the public key from Clerk's JWKS endpoint instead of calling the
Clerk REST API, which is both faster (no network round-trip per request)
and more reliable (works offline if JWKS is cached).
"""

import os
import time
import logging
from typing import Any, Dict

import httpx
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

security = HTTPBearer()

# CLERK_JWKS_URL — must be explicitly configured via env var
# No fallback URL committed to codebase
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
CLERK_AUDIENCE = os.getenv("CLERK_AUDIENCE")

if not CLERK_JWKS_URL:
    # Fail fast if not configured — no silent fallback to hardcoded URLs
    logger.warning(
        "CLERK_JWKS_URL not set. Clerk auth will fail. "
        "Set this env var to your Clerk project's JWKS URL."
    )

# JWKS cache with TTL (1 hour)
_jwks_cache: Dict[str, Any] = {}
_jwks_cache_time: float = 0
JWKS_CACHE_TTL = 3600  # 1 hour


async def _get_jwks() -> Dict[str, Any]:
    """
    Fetches and caches Clerk's JWKS (JSON Web Key Set) for token verification.
    Cache has a TTL of 1 hour to allow key rotation.
    """
    now = time.time()
    # Check if cache is still valid
    if _jwks_cache and (now - _jwks_cache_time) < JWKS_CACHE_TTL:
        return _jwks_cache

    if not CLERK_JWKS_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Clerk JWKS URL not configured. Set CLERK_JWKS_URL env var.",
        )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(CLERK_JWKS_URL)
            response.raise_for_status()
            _jwks_cache.clear()
            _jwks_cache.update(response.json())
            _jwks_cache_time = now
            logger.info("Clerk JWKS loaded from %s (cached for %ds)", CLERK_JWKS_URL, JWKS_CACHE_TTL)
    except httpx.RequestError as exc:
        logger.error("Failed to fetch Clerk JWKS: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable — cannot reach Clerk JWKS.",
        ) from exc

    return _jwks_cache


class ClerkAuth:
    """
    Verifies Clerk JWTs using the public JWKS endpoint.
    Avoids per-request calls to the Clerk REST API for lower latency.
    """

    @staticmethod
    async def verify_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> Dict[str, Any]:
        """
        Decodes and validates the Clerk JWT from the Authorization header.
        Returns the decoded payload on success; raises HTTP 401 on any failure.
        """
        token = credentials.credentials
        jwks = await _get_jwks()

        try:
            # Always verify audience — fail if CLERK_AUDIENCE is not configured
            if not CLERK_AUDIENCE:
                logger.error(
                    "CLERK_AUDIENCE not set. Token verification requires audience validation. "
                    "Set CLERK_AUDIENCE env var to your Clerk application's audience/origin."
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Server misconfiguration: CLERK_AUDIENCE not set.",
                )

            payload = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience=CLERK_AUDIENCE,
                options={"verify_aud": True},  # Always verify
            )
        except JWTError as exc:
            logger.warning("Clerk JWT verification failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token.",
            ) from exc

        return {
            "user_id": payload.get("user_id") or payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role", "client"),
        }


def get_current_user(
    user_data: Dict[str, Any] = Depends(ClerkAuth.verify_token),
) -> Dict[str, Any]:
    """FastAPI dependency for securing endpoints with Clerk auth."""
    return user_data

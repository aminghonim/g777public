"""
Clerk JWT Authentication — Verifies tokens using the JWKS endpoint.

Uses the public key from Clerk's JWKS endpoint instead of calling the
Clerk REST API, which is both faster (no network round-trip per request)
and more reliable (works offline if JWKS is cached).
"""

import os
import logging
from typing import Any, Dict

import httpx
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

security = HTTPBearer()

CLERK_JWKS_URL = os.getenv(
    "CLERK_JWKS_URL",
    "https://credible-kingfish-86.clerk.accounts.dev/.well-known/jwks.json",
)

_jwks_cache: Dict[str, Any] = {}


async def _get_jwks() -> Dict[str, Any]:
    """
    Fetches and caches Clerk's JWKS (JSON Web Key Set) for token verification.
    Cached in memory so each process only fetches once at startup.
    """
    if _jwks_cache:
        return _jwks_cache

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(CLERK_JWKS_URL)
            response.raise_for_status()
            _jwks_cache.update(response.json())
            logger.info("Clerk JWKS loaded from %s", CLERK_JWKS_URL)
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
            payload = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                options={"verify_aud": False},
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

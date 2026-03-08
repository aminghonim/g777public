import os
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from loguru import logger

# 🛡️ CNS SQUAD MANDATE: Rule 12 (Tenant Shield)
# This module handles Clerk JWT verification and user extraction.

security = HTTPBearer()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_API_BASE = "https://api.clerk.dev/v1"

class ClerkAuth:
    """
    Handles authentication via Clerk.
    Verifies the JWT token and extracts user information.
    """
    
    @staticmethod
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        if not CLERK_SECRET_KEY:
            logger.error("CLERK_SECRET_KEY is missing in .env")
            raise HTTPException(status_code=500, detail="Auth configuration error")

        try:
            # Check with Clerk API to verify our session
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {CLERK_SECRET_KEY}"}
                # Verification using Clerk's backend API (User Introspection)
                # This ensures the session is currently valid on Clerk's servers.
                response = await client.get(
                    f"{CLERK_API_BASE}/users/me", # Clerk's standard "Who am I?" endpoint
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code != 200:
                    logger.warning(f"Clerk token verification failed: {response.text}")
                    raise HTTPException(status_code=401, detail="Invalid Clerk session")
                
                user_data = response.json()
                # 🛡️ Rule 12: Attach user_id to context for tenant isolation
                return {
                    "user_id": user_data.get("id"),
                    "email": user_data.get("email_addresses")[0].get("email_address") if user_data.get("email_addresses") else None,
                    "status": "active"
                }

        except Exception as e:
            logger.error(f"Clerk verification error: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

def get_current_user(user_data: dict = Depends(ClerkAuth.verify_token)):
    """
    Dependency to be used in secure routes.
    Ensures Rule 12 (Tenant Isolation) can be applied by providing user context.
    """
    return user_data

from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.security import SecurityEngine

# Initialize scheme here to be reused
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Dict[str, Any]:
    """
    SAAS-007: Strict SaaS User Dependency.
    Ensures every secure request has a validated user_id and instance_name.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )
    try:
        # The decode_token now validates 'sub', 'instance_name' existence and blocklist (V7.4.1)
        payload = SecurityEngine.decode_token(credentials.credentials)
        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(exc)}",
        )

"""
G777 Security Middleware - Modular Traffic Control
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from core.config import settings
from core.security import SecurityEngine


async def secure_handshake_middleware(request: Request, call_next):
    """
    Validates the G777 Handshake Token for all non-exempt requests.
    """
    # 1. Bypass exempt paths and OPTIONS requests
    if request.url.path in settings.system.exempt_paths or request.method == "OPTIONS":
        return await call_next(request)

    # 2. Extract and Validate Token
    handshake_token = request.headers.get(settings.security.token_header)
    session = SecurityEngine.get_current_session()

    if not session or handshake_token != session.get("token"):
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized: Invalid or missing G777 Handshake Token"},
        )

    # 3. Proceed to the next handler
    return await call_next(request)

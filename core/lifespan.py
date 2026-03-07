"""
G777 Lifespan Manager - Modular Startup/Shutdown Logic
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.security import SecurityEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Antigravity Lifespan Manager.
    Handles secure handshake initialization and background checks.
    """
    from backend.startup_checks import validate_webhook_reachability

    # 1. Create secure session lock (Dynamic Port & Token)
    SecurityEngine.create_session_lock()

    # 2. Run modular startup checks
    validate_webhook_reachability()

    yield

    # 3. Clean up session on shutdown
    SecurityEngine.cleanup_session()

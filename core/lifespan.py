"""
G777 Lifespan Manager - Modular Startup/Shutdown Logic
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.security import SecurityEngine

logger = logging.getLogger(__name__)

async def supabase_keep_alive():
    """Background task to ping Supabase to prevent auto-pause."""
    from backend.database_manager import DatabaseManager
    while True:
        try:
            db_manager = DatabaseManager()
            if not db_manager.is_sqlite:
                conn = db_manager.get_connection()
                if conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1")
                    db_manager.release_connection(conn)
                    logger.debug("❤️ Supabase Heartbeat: SELECT 1 successful.")
        except asyncio.CancelledError:
            # Expected on shutdown
            break
        except Exception as e:
            logger.error(f"Supabase Heartbeat Failed: {e}")
        
        try:
            # Ping every 15 minutes (900 seconds)
            await asyncio.sleep(900)
        except asyncio.CancelledError:
            break


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Antigravity Lifespan Manager.
    Handles secure handshake initialization and background checks.
    """
    from backend.startup_checks import validate_webhook_reachability
    from backend.database_manager import db_manager

    # 1. Create secure session lock (Dynamic Port & Token)
    SecurityEngine.create_session_lock()

    # 2. Run modular startup checks
    validate_webhook_reachability()

    # 3. Run database migrations (licenses, devices, tiers, users)
    db_manager.check_migrations()
    logger.info("Database migrations completed successfully.")

    # 4. Start Supabase Keep-Alive Heartbeat
    keep_alive_task = asyncio.create_task(supabase_keep_alive())

    yield

    # 4. Clean up session and tasks on shutdown
    keep_alive_task.cancel()
    SecurityEngine.cleanup_session()

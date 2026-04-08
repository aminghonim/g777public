import os
import psutil
import logging
from fastapi import APIRouter, HTTPException
from backend.database_manager import DatabaseManager
from backend.memory.vector_store_manager import VectorStoreManager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """
    Active Health Check for Backend Infrastructure.
    """
    checks_status = {}
    health_status = {"status": "healthy", "checks": checks_status}
    
    # 1. System Health
    try:
        checks_status["system"] = {
            "status": "up",
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "pid": os.getpid()
        }
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        checks_status["system"] = {"status": "down", "error": str(e)}
        health_status["status"] = "unhealthy"

    # 2. Database Health
    try:
        db_manager = DatabaseManager()
        app_conn = db_manager.get_connection()
        if hasattr(db_manager, "is_mock") and db_manager.is_mock:
            # Ping SQLite Mock
            cursor = app_conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        else:
            # Ping PostgreSQL Supabase
            cursor = app_conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            db_manager.release_connection(app_conn)
        checks_status["database"] = {"status": "up"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks_status["database"] = {"status": "down", "error": str(e)}
        health_status["status"] = "unhealthy"

    # 3. Vector DB Health
    try:
        vector_db = VectorStoreManager()
        # Ping ChromaDB collection
        collection = getattr(vector_db, "collection", None)
        if collection:
            _ = collection.count()
        checks_status["vector_db"] = {"status": "up"}
    except Exception as e:
        logger.error(f"Vector DB health check failed: {e}")
        checks_status["vector_db"] = {"status": "down", "error": str(e)}
        health_status["status"] = "unhealthy"

    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status

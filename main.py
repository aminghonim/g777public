"""
G777 Antigravity - Main Entry Point
Version: 2.2.0 | Flutter Edition
Mandate: Modular & Transparent Orchestration
"""

# 🛡️ CNS SQUAD MANDATE: Zero-Regression & Full Quality Audit (Activated)

# =====================================================================
# RTK Enforcement Guard - Runtime Blocker (CRITICAL - Must be first)
# =====================================================================
from backend.core.rtk_enforcement import setup_rtk_enforcement

setup_rtk_enforcement()

import os
from dotenv import load_dotenv

# Load .env BEFORE any other imports to fix SECRET_KEY and ENV issues
load_dotenv()

import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Core Configuration & Security
from core.config import settings
from core.security import SecurityEngine
from core.lifespan import lifespan
from core.middleware import secure_handshake_middleware, license_expiry_middleware
from api.router_registry import register_all_routers
from backend.core.monitoring import init_monitoring
from _version import __version__

# 1. Initialize Sentry/Monitoring
init_monitoring()

# 2. Initialize FastAPI Application
app = FastAPI(
    title=settings.system.app_name,
    version=settings.system.version,
    lifespan=lifespan,
    docs_url="/api/docs" if "--dev" in sys.argv else None,
)

# 3. Apply Middlewares (order matters: handshake first, then license check)
app.middleware("http")(secure_handshake_middleware)
app.middleware("http")(license_expiry_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.network.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Register Modular API Routers
register_all_routers(app)


# 5. Global Health Monitoring (Track 2)
@app.get("/health")
async def health_check():
    return {
        "status": "active",
        "version": __version__,
        "mode": settings.system.environment,
        "pid": os.getpid(),
    }


# 6. Execution Loop
if __name__ == "__main__":
    # Priority: ENV PORT -> Settings Default -> Fallback 8000
    port = int(os.getenv("PORT", settings.network.default_port or 8000))

    # Explicitly set PORT in env so the SecurityEngine (called in lifespan) sees it
    os.environ["PORT"] = str(port)

    uvicorn.run(
        "main:app",
        host=settings.network.host,
        port=port,
        reload="--dev" in sys.argv,
        log_level="info" if "--dev" in sys.argv else "warning",
    )

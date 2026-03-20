\"\"\"
G777 Antigravity - Main Entry Point
Version: 2.2.0 | Flutter Edition
Mandate: Modular & Transparent Orchestration
\"\"\"

# 🛡️ CNS SQUAD MANDATE: Zero-Regression & Full Quality Audit (Activated)

import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Core Configuration & Security
from core.config import settings
from core.security import SecurityEngine
from core.lifespan import lifespan
from core.middleware import secure_handshake_middleware
from api.router_registry import register_all_routers
from backend.core.monitoring import init_monitoring
# 1. Initialize Sentry/Monitoring
init_monitoring()

__version__ = \"2.2.0\"

# 2. Initialize FastAPI Application
app = FastAPI(
    title=settings.system.app_name,
    version=settings.system.version,
    lifespan=lifespan,
    docs_url=\"/api/docs\" if \"--dev\" in sys.argv else None,
)

# 3. Apply Middlewares
app.middleware(\"http\")(secure_handshake_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.network.cors_origins,
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

# 4. Register Modular API Routers
register_all_routers(app)


from backend.utils.health import router as health_router

# 5. Global Health Monitoring (Track 2)
app.include_router(health_router)


# 6. Execution Loop
if __name__ == \"__main__\":
    # Priority: ENV PORT -> Settings Default -> Fallback 8000
    port = int(os.getenv(\"PORT\", settings.network.default_port or 8000))

    # Explicitly set PORT in env so the SecurityEngine (called in lifespan) sees it
    os.environ[\"PORT\"] = str(port)

    uvicorn.run(
        \"main:app\",
        host=settings.network.host,
        port=port,
        reload=\"--dev\" in sys.argv,
        log_level=\"info\" if \"--dev\" in sys.argv else \"warning\",
    )
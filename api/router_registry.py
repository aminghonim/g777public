from fastapi import FastAPI
from backend.routers import (
    analytics,
    campaigns,
    connector,
    crm,
    evolution,
    intelligence,
    license,
    system,
    users,
    warmer,
    web_ui
)

def register_all_routers(app: FastAPI):
    """
    Registers all modular routers from the backend directory.
    This reconstructs the missing api/router_registry implementation.
    """
    # System & Core
    app.include_router(system.router, tags=["System"])
    app.include_router(users.router, tags=["Users"])
    app.include_router(license.router, tags=["License"])
    
    # Business Modules
    app.include_router(crm.router, prefix="/api/crm", tags=["CRM"])
    app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
    app.include_router(connector.router, prefix="/api/connector", tags=["Connectors"])
    app.include_router(intelligence.router, prefix="/api/intelligence", tags=["Intelligence"])
    app.include_router(evolution.router, prefix="/api/evolution", tags=["Evolution"])
    app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
    app.include_router(warmer.router, prefix="/api/warmer", tags=["Warmer"])
    
    # UI Endpoints
    app.include_router(web_ui.router, tags=["Web UI"])

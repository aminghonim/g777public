"""
G777 Router Registry - المركز الرئيسي لتسجيل كافة المسارات
Centralizes all API route registrations to keep main.py clean and modular.
"""

from fastapi import FastAPI
from . import (
    group_sender,
    members_grabber,
    number_filter,
    cloud_hub,
    wa_hub,
    account_warmer,
    automation_hub,
    links_grabber,
    maps_extractor,
    poll_sender,
    social_extractor,
)
from backend.webhook_handler import router as webhook_router


def register_all_routers(app: FastAPI):
    """ثبت كل الموديولات في تطبيق FastAPI"""

    # Core Webhooks
    app.include_router(webhook_router)

    # SAAS Modules (User & License & Evolution)
    from backend.routers.evolution import router as evolution_router
    from backend.routers.users import router as users_router
    from backend.routers.license import router as license_router
    from backend.routers.analytics import router as analytics_router
    from backend.routers.system import router as system_router
    from backend.routers.intelligence import router as intelligence_router
    from backend.routers.connector import router as connector_router

    app.include_router(evolution_router, prefix="/evolution", tags=["Evolution SaaS"])
    app.include_router(users_router, prefix="/users", tags=["User Profiles & Quotas"])
    app.include_router(license_router, prefix="/auth/license", tags=["License Engine"])
    app.include_router(
        analytics_router, prefix="/analytics", tags=["Dashboard & Analytics"]
    )
    app.include_router(
        intelligence_router, prefix="/intelligence", tags=["AI Intelligence"]
    )
    app.include_router(
        connector_router, prefix="/connector", tags=["System Connectors"]
    )
    app.include_router(system_router)

    # G777 Modules
    app.include_router(group_sender.router)
    app.include_router(members_grabber.router)
    app.include_router(number_filter.router)
    app.include_router(cloud_hub.router)  # legacy shim kept for backward-compat
    app.include_router(wa_hub.router)
    app.include_router(account_warmer.router)
    app.include_router(automation_hub.router)
    app.include_router(links_grabber.router)
    app.include_router(maps_extractor.router)
    app.include_router(poll_sender.router)
    app.include_router(social_extractor.router)

    print("[OK] All G777 API Routers Registered Successfully")

from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import get_current_user
from backend.database_manager import db_manager
from backend.core.security_sanitizer import SecuritySanitizer
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dashboard")
async def get_dashboard_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    SAAS-018: Secure Dashboard Analytics Endpoint.
    Aggregates lifetime and recent metrics for the authenticated tenant.
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID missing from token")

    # ASVS V5: Sanitize input
    sanitized_user_id = SecuritySanitizer.sanitize_input(user_id)

    try:
        stats = db_manager.get_dashboard_analytics(sanitized_user_id)
        if not stats:
            return {
                "total_messages_sent": 0,
                "daily_usage": 0,
                "daily_limit": 100,
                "daily_remaining": 100,
                "active_instances": 0,
                "max_instances": 1,
                "activity_7d": [],
            }
        return stats
    except Exception as e:
        logger.error(f"[REDACTED ERROR] Analytics failure for {sanitized_user_id}: {e}")
        # ASVS V16.5.1: Generic error for public consumption
        raise HTTPException(
            status_code=500,
            detail="Internal error while retrieving analytics dashboard data.",
        )

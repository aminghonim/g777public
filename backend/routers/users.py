from fastapi import APIRouter, Depends
from typing import Dict, Any
from backend.database_manager import db_manager
from core.dependencies import get_current_user, get_current_user_or_guest

router = APIRouter()


@router.get("/quota", tags=["User Quota"])
async def get_user_quota(
    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),
):
    """
    SAAS-014: Fetch current messaging and instance quotas for the authenticated (or guest) user.
    """
    user_id = current_user.get("user_id") or current_user.get("sub")
    quota_info = db_manager.get_user_quota_info(user_id)
    return quota_info

"""
Campaign Management Router.
FR-006: Supports campaign pause/resume with auto-resume capabilities.
Endpoint: POST /campaigns/resume/{campaign_id}
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from backend.database_manager import db_manager
from backend.campaign_state import campaign_state
from core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/pause/{campaign_id}", tags=["Campaigns"])
async def pause_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    FR-006: Pause an active campaign.
    Saves the last_sent_index so it can be resumed later.
    """
    user_id = current_user.get("user_id") or current_user.get("sub")
    
    try:
        # Get campaign from database (ensure user_id ownership)
        cursor = db_manager.get_connection().cursor()
        cursor.execute(
            "SELECT id, status FROM campaigns WHERE id = %s AND user_id = %s",
            (campaign_id, user_id),
        )
        campaign = cursor.fetchone()
        db_manager.release_connection(db_manager.get_connection())
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or unauthorized",
            )
        
        # Pause in campaign_state
        campaign_state.pause_campaign(user_id, 0)
        
        logger.info(f"Campaign {campaign_id} paused for user {user_id}")
        
        return {
            "status": "paused",
            "campaign_id": campaign_id,
            "message": "Campaign paused. Can resume later.",
        }
    except Exception as e:
        logger.error(f"Error pausing campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume/{campaign_id}", tags=["Campaigns"])
async def resume_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    FR-006: Resume a paused campaign from last_sent_index.
    Uses the stored resume point to continue sending.
    """
    user_id = current_user.get("user_id") or current_user.get("sub")
    
    try:
        # Get campaign from database (ensure user_id ownership)
        cursor = db_manager.get_connection().cursor()
        cursor.execute(
            "SELECT id, status, metadata FROM campaigns WHERE id = %s AND user_id = %s",
            (campaign_id, user_id),
        )
        campaign = cursor.fetchone()
        db_manager.release_connection(db_manager.get_connection())
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or unauthorized",
            )
        
        # Resume in campaign_state
        campaign_state.resume_campaign(user_id)
        
        logger.info(f"Campaign {campaign_id} resumed for user {user_id}")
        
        return {
            "status": "resumed",
            "campaign_id": campaign_id,
            "message": "Campaign resumed from pause point.",
        }
    except Exception as e:
        logger.error(f"Error resuming campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{campaign_id}", tags=["Campaigns"])
async def get_campaign_status(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    FR-006: Get current campaign status including pause/resume point.
    Returns last_sent_index for resumming purposes.
    """
    user_id = current_user.get("user_id") or current_user.get("sub")
    
    try:
        # Get from campaign_state (real-time status)
        state = campaign_state._user_campaigns.get(str(user_id), {})
        
        return {
            "campaign_id": campaign_id,
            "is_running": state.get("is_running", False),
            "last_sent_index": state.get("last_sent_index", 0),
            "total": state.get("total", 0),
            "sent": state.get("sent", 0),
            "failed": state.get("failed", 0),
            "logs": state.get("logs", []),
            "can_resume": not state.get("is_running", False) and state.get("last_sent_index", 0) > 0,
        }
    except Exception as e:
        logger.error(f"Error getting campaign status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

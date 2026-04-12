import logging
from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Optional, Dict, Any
from backend.services.group_sender_service import GroupSenderService
from backend.models.group_sender import GroupBroadcastRequest, GroupSyncResponse
from backend.core.auth import get_current_user

router = APIRouter(prefix="/groups", tags=["Group Sender"])
logger = logging.getLogger(__name__)

@router.get("/sync", response_model=GroupSyncResponse)
async def sync_groups(
    x_instance_name: Optional[str] = Header(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    if not x_instance_name:
        raise HTTPException(status_code=400, detail="X-Instance-Name header required")
    
    service = GroupSenderService(instance_name=x_instance_name)
    groups = service.sync_groups()
    return {"success": True, "groups": groups}

@router.post("/broadcast")
async def broadcast_message(
    request: GroupBroadcastRequest, 
    x_instance_name: Optional[str] = Header(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    if not x_instance_name:
        raise HTTPException(status_code=400, detail="X-Instance-Name header required")
    
    user_id = current_user.get("user_id") or "global"
    service = GroupSenderService(instance_name=x_instance_name)
    await service.start_broadcast(
        group_ids=request.group_ids,
        message=request.message,
        delay_min=request.delay_min,
        delay_max=request.delay_max,
        user_id=user_id
    )
    return {"success": True, "message": "Broadcast started"}

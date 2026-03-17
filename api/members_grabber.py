from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pathlib import Path

from ui.controllers.members_grabber_controller import MembersGrabberController
from core.dependencies import get_current_user

router = APIRouter(prefix="/api/members-grabber", tags=["Members Grabber"])
controller = MembersGrabberController()


@router.get("/groups")
async def get_groups(user: Dict[str, Any] = Depends(get_current_user)):
    """Fetch all groups from user's WhatsApp instance"""
    instance_name = user.get("instance_name")
    groups = await controller.fetch_groups(instance_name=instance_name)
    return groups


@router.get("/groups/{jid}/members")
async def get_members(jid: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Grab members from a specific group in user's instance"""
    instance_name = user.get("instance_name")
    members = await controller.grab_members(jid, instance_name=instance_name)
    return members


@router.post("/export")
async def export_members(
    members: List[Dict], user: Dict[str, Any] = Depends(get_current_user)
):
    """Export provided members list to excel (SaaS-Safe)"""
    user_id = str(user.get("user_id"))
    export_dir = Path("uploads") / user_id / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    file_name = "grabbed_members.xlsx"
    file_path = str(export_dir / file_name)
    result_path = controller.export_to_excel(members, file_path)

    if not result_path:
        raise HTTPException(status_code=400, detail="Failed to export members")

    return {"path": result_path, "filename": file_name}

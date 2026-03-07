from fastapi import APIRouter, Body, Depends, HTTPException
from typing import List, Optional, Dict, Any
from ui.controllers.poll_sender_controller import PollSenderController
from core.dependencies import get_current_user

router = APIRouter(prefix="/api/poll-sender", tags=["Poll Sender"])
controller = PollSenderController()


@router.post("/send")
async def send_poll(
    question: str = Body(...),
    options: List[str] = Body(...),
    excel_file: Optional[str] = Body(None),
    user: Dict[str, Any] = Depends(get_current_user),
):
    """Send a WhatsApp poll using user's instance (SaaS-Ready)"""
    instance_name = user.get("instance_name")
    # Note: controller.send_poll needs to be checked/updated for instance_name support
    try:
        await controller.send_poll(
            question, options, excel_file, instance_name=instance_name
        )
        return {"status": "success", "message": "Poll sequence initiated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status(user: Dict[str, Any] = Depends(get_current_user)):
    """Get status for current user (Scoped via instance if possible)"""
    # For now returns global controller state, but should be user-scoped in controller refactor
    return {"is_sending": controller.state["is_sending"]}

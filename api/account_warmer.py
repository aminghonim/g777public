from fastapi import APIRouter, Body
from typing import Optional, List
from ui.controllers.account_warmer_controller import AccountWarmerController

router = APIRouter(prefix="/api/account-warmer", tags=["Account Warmer"])
controller = AccountWarmerController()

@router.post("/start")
async def start_warming(
    phone1: str = Body(...),
    phone2: str = Body(...),
    count: int = Body(50),
    delay: int = Body(60)
):
    """Start the warming loop between two accounts"""
    # Note: This is an async process. For now, we'll run it in the background.
    # In a full production app, we would use a task queue like Celery or a background task.
    import asyncio
    asyncio.create_task(controller.start_warming(phone1, phone2, count, delay))
    return {"status": "started", "message": f"Warming {count} messages initiated."}

@router.post("/stop")
async def stop_warming():
    """Stop the running warming cycle"""
    controller.stop_warming()
    return {"status": "stopped"}

@router.get("/logs")
async def get_logs():
    """Get the current warming logs"""
    return {"logs": controller.get_logs(), "state": controller.state}

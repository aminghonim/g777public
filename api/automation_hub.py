from fastapi import APIRouter
from ui.controllers.automation_hub_controller import AutomationHubController

router = APIRouter(prefix="/api/automation-hub", tags=["Automation Hub"])
controller = AutomationHubController()

@router.get("/instance")
async def get_instance_info():
    """Get instance connection status and metadata"""
    return controller.get_instance_info()

@router.get("/stats")
async def get_stats():
    """Get high-level automation statistics"""
    return controller.get_stats()

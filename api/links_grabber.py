from fastapi import APIRouter, Body
from typing import List, Dict
from ui.controllers.links_grabber_controller import LinksGrabberController

router = APIRouter(prefix="/api/links-grabber", tags=["Links Grabber"])
controller = LinksGrabberController()

@router.post("/hunt")
async def start_hunt(
    keyword: str = Body(...),
    count: int = Body(10)
):
    """Run the group finding process (Selenium background task)"""
    results = await controller.run_hunt(keyword, count)
    return results

@router.delete("/clear")
async def clear_results():
    """Clear all results"""
    controller.clear_results()
    return {"status": "cleared"}

@router.get("/results")
async def get_results():
    """Get current results"""
    return {"results": controller.state['results'], "is_hunting": controller.state['is_hunting']}

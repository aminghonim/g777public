from fastapi import APIRouter, Body
from typing import List, Dict
from ui.controllers.social_extractor_controller import SocialExtractorController

router = APIRouter(prefix="/api/social-extractor", tags=["Social Extractor"])
controller = SocialExtractorController()

@router.post("/extract")
async def start_extraction(
    keyword: str = Body(...),
    limit: int = Body(20),
    scrolling_depth: int = Body(2)
):
    """Run the social media contact extraction process"""
    results = await controller.run_extraction(keyword, limit, scrolling_depth)
    return results

@router.get("/results")
async def get_results():
    """Get current extraction results"""
    return {"results": controller.state['results'], "is_extracting": controller.state['is_extracting']}

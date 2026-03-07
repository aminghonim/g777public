from fastapi import APIRouter, Body
from ui.controllers.maps_extractor_controller import MapsExtractorController

router = APIRouter(prefix="/api/maps-extractor", tags=["Maps Extractor"])
controller = MapsExtractorController()


@router.post("/extract")
async def start_extraction(
    query: str = Body(...),
    location: str = Body(...),
    max_results: int = Body(50),
    scrolling_depth: int = Body(2),
):
    """Run the Google Maps business extraction process"""
    results = await controller.run_extraction(
        query, location, max_results, scrolling_depth
    )
    return results


@router.get("/suggestions")
async def get_suggestions():
    """Get trending target suggestions for maps extraction"""
    return {"suggestions": controller.get_suggestions()}


@router.get("/results")
async def get_results():
    """Get current extraction results"""
    return {
        "results": controller.state["results"],
        "is_extracting": controller.state["is_extracting"],
    }

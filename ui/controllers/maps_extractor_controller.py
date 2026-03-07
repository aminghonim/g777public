import asyncio
from typing import List, Dict
from backend.maps_extractor import MapsExtractor


class MapsExtractorController:
    """
    Controller for Google Maps Extractor UI.
    Bridge to MapsExtractor backend.
    """

    def __init__(self):
        self.state = {"results": [], "is_extracting": False}
        self.extractor = MapsExtractor()

    async def run_extraction(
        self, query: str, location: str, max_results: int, scrolling_depth: int = 2
    ) -> List[Dict]:
        """Runs the extraction process."""
        if self.state["is_extracting"]:
            return []

        self.state["is_extracting"] = True
        try:
            # The backend search_businesses is now async
            results = await self.extractor.search_businesses(
                query, location, max_results, scrolling_depth
            )
            self.state["results"] = results if results else []
            return self.state["results"]
        finally:
            self.state["is_extracting"] = False

    def get_suggestions(self) -> List[str]:
        """Gets trending target suggestions."""
        return self.extractor.get_smart_suggestions()

import logging
from typing import List, Dict
from backend.market_intelligence.sources.social_scraper import SocialScraper


class SocialExtractorController:
    """
    Controller for Social Media Extractor UI.
    Connects UI to the SocialScraper Dorking engine.
    """

    def __init__(self):
        self.state = {"is_extracting": False, "results": [], "error": None}
        self.scraper = SocialScraper()

    async def run_extraction(
        self, keyword: str, limit: int = 20, scrolling_depth: int = 2
    ) -> List[Dict]:
        """Runs the real extraction logic via Dorking engine."""
        if self.state["is_extracting"]:
            return []

        self.state["is_extracting"] = True
        self.state["error"] = None

        try:
            # The scraper.scrape is now async
            response = await self.scraper.scrape(keyword, limit, scrolling_depth)

            if response.get("success"):
                self.state["results"] = response.get("results", [])
                return self.state["results"]
            else:
                self.state["error"] = response.get("error", "Unknown Error")
                self.state["results"] = []
                return []
        except Exception as e:
            self.state["error"] = str(e)
            return []
        finally:
            self.state["is_extracting"] = False

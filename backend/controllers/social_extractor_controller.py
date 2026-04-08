"""
Social Extractor Controller - Pure Backend Logic.
Manages asynchronous social media data extraction.
"""

import logging
from typing import Dict, Any
from backend.market_intelligence.sources.social_scraper import SocialScraper

# CNS Logging Compliance
logger = logging.getLogger(__name__)

class SocialExtractorController:
    """Manages context-aware social media scraping operations."""

    def __init__(self):
        self.scraper = SocialScraper()
        self.state: Dict[str, Any] = {"results": [], "is_extracting": False}

    async def run_extraction(self, keyword: str, limit: int, depth: int) -> Dict[str, Any]:
        """Initiates the scraping process using SocialScraper."""
        self.state["is_extracting"] = True
        try:
            # depth: int is part of the request but might be used as limit or secondary param
            # current SocialScraper.scrape only takes keyword and limit
            response = self.scraper.scrape(keyword, limit=limit)
            if response.get("success"):
                self.state["results"] = response.get("results", [])
            return response
        except (RuntimeError, ConnectionError, ValueError) as e:
            logger.error("Social Extractor Error: %s", e)
            return {"success": False, "error": str(e)}
        finally:
            self.state["is_extracting"] = False

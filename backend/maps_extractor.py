"""
Google Maps Extractor Module
Handles business data extraction from Google Maps.
"""


class MapsExtractor:
    """
    Handles extraction of business information from Google Maps.

    Features:
    - Extract business names
    - Extract phone numbers
    - Extract addresses
    - Search by category/location
    """

    def __init__(self):
        """Initialize the MapsExtractor with default configuration."""
        from .market_intelligence.core import MarketIntelligenceManager

        self.market_intel = MarketIntelligenceManager()

        # Import the real scraper
        from .market_intelligence.sources.maps_extractor import (
            MapsExtractor as InnerMapsExtractor,
        )

        self.scraper = InnerMapsExtractor(headless=True)

    def get_smart_suggestions(self):
        """Fetches trending search queries from Market Intelligence."""
        return self.market_intel.get_scraping_targets()

    async def search_businesses(
        self, query: str, location: str, max_results: int = 50, scrolling_depth: int = 2
    ):
        """
        Search for businesses on Google Maps.
        """
        search_term = f"{query} in {location}"
        result = await self.scraper.scrape(
            search_term, limit=max_results, scrolling_depth=scrolling_depth
        )
        return result.get("results", [])

    def extract_business_name(self, business_element):
        """
        Extract business name from a Google Maps listing element.
        """
        return "Not Implemented - Handled by Scraper"

    def extract_phone_number(self, business_element):
        """
        Extract phone number from a Google Maps listing element.
        """
        return "Not Implemented - Handled by Scraper"

    def extract_address(self, business_element):
        """
        Extract address from a Google Maps listing element.
        """
        return "Not Implemented - Handled by Scraper"

    def export_to_excel(self, business_data, output_path):
        """
        Export extracted business data to Excel file.
        """
        import pandas as pd

        if not business_data:
            return False
        df = pd.DataFrame(business_data)
        df.to_excel(output_path, index=False)
        return True

    def clean_phone_number(self, raw_number):
        """
        Clean and format phone number to international format.
        """
        import re

        if not raw_number:
            return ""
        # Remove non-numeric characters except +
        cleaned = re.sub(r"[^\d+]", "", raw_number)
        return cleaned

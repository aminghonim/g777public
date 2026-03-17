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
        from .market_intelligence.core import MarketIntelligenceManager  # pylint: disable=import-outside-toplevel

        self.market_intel = MarketIntelligenceManager()

        # Import the real scraper
        from .market_intelligence.sources.maps_extractor import (  # pylint: disable=import-outside-toplevel
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
        Search for businesses on Google Maps. Includes a free fallback to OpenStreetMap Nominatim.
        """
        search_term = f"{query} in {location}"
        try:
            result = await self.scraper.scrape(
                search_term, limit=max_results, scrolling_depth=scrolling_depth
            )
            if result and result.get("results"):
                return result.get("results")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(
                f"[MapsExtractor] Scraper failed: {e}. Falling back to Nominatim API..."
            )

        # --- Fallback: OpenStreetMap Nominatim API ---
        return await self._nominatim_fallback_search(query, location, max_results)

    async def _nominatim_fallback_search(
        self, query: str, location: str, max_results: int
    ):
        import aiohttp  # pylint: disable=import-outside-toplevel,import-error
        import asyncio  # pylint: disable=import-outside-toplevel
        from backend.core.utils.api_helpers import load_api_config  # pylint: disable=import-outside-toplevel

        config = load_api_config().get("apis", {}).get("maps_nominatim", {})
        url = config.get("base_url", "https://nominatim.openstreetmap.org/search")
        rate_limit_ms = config.get("rate_limit_ms", 1050)
        user_agent = config.get("user_agent", "G777_Project_DataTool/1.0 (contact@yourdomain.com)")
        params = {
            "q": f"{query} {location}",
            "format": "json",
            "addressdetails": 1,
            "extratags": 1,
            "limit": max_results,
        }
        headers = {"User-Agent": user_agent}

        # --- Strict Rate Limiting (Nominatim Usage Policy) ---
        await asyncio.sleep(rate_limit_ms / 1000.0)
        # -----------------------------------------------------

        results = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, headers=headers, timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data:
                            # Map Nominatim response to expected format
                            phone = item.get("extratags", {}).get("phone", "")
                            if not phone:
                                phone = item.get("extratags", {}).get(
                                    "contact:phone", ""
                                )

                            results.append(
                                {
                                    "name": item.get("name", "Unknown Business"),
                                    "phone": (
                                        self.clean_phone_number(phone)
                                        if phone
                                        else "N/A"
                                    ),
                                    "address": item.get("display_name", ""),
                                    "source": "OpenStreetMap (Fallback)",
                                }
                            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"[MapsExtractor] Nominatim fallback also failed: {e}")

        return results

    def extract_business_name(self, _business_element):  # pylint: disable=unused-argument
        """
        Extract business name from a Google Maps listing element.
        """
        return "Not Implemented - Handled by Scraper"

    def extract_phone_number(self, _business_element):  # pylint: disable=unused-argument
        """
        Extract phone number from a Google Maps listing element.
        """
        return "Not Implemented - Handled by Scraper"

    def extract_address(self, _business_element):  # pylint: disable=unused-argument
        """
        Extract address from a Google Maps listing element.
        """
        return "Not Implemented - Handled by Scraper"

    def export_to_excel(self, business_data, output_path):
        """
        Export extracted business data to Excel file.
        """
        import pandas as pd  # pylint: disable=import-outside-toplevel,import-error

        if not business_data:
            return False
        df = pd.DataFrame(business_data)
        df.to_excel(output_path, index=False)
        return True

    def clean_phone_number(self, raw_number):
        """
        Clean and format phone number to international format.
        """
        import re  # pylint: disable=import-outside-toplevel

        if not raw_number:
            return ""
        # Remove non-numeric characters except +
        cleaned = re.sub(r"[^\d+]", "", raw_number)
        return cleaned

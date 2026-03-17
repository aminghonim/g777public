import asyncio
import logging
import urllib.parse
from typing import List, Dict, Any, Optional
import yaml
import os
from tenacity import retry, stop_after_attempt, wait_exponential
from playwright.async_api import async_playwright, Browser, Page, Route
from services.maps_scraper.engine import BrowserFactory
from services.maps_scraper.stealth import StealthManager
from services.maps_scraper.parser import MapsDataParser

class MapsScraper:
    """
    Core Scraper Logic (Phase 2).
    Implements High-Speed Network Interception & Stealth navigation.
    """

    def __init__(self, config_path: str = "config/maps_scraper.yaml"):
        # Explicitly setting absolute path if inside container
        self.config_path = config_path
        if not os.path.exists(config_path):
            # Fallback for different execution contexts
            config_path = "/app/config/maps_scraper.yaml"
            
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.logger = logging.getLogger("MapsScraper")
        self.logger.setLevel(logging.INFO)
        self.stealth = StealthManager(config_path)
        self.parser = MapsDataParser()
        self.factory = BrowserFactory(config_path)
        self.raw_responses = []

    async def _intercept_response(self, response):
        """
        Intercepts network responses to capture Google Maps business data.
        """
        try:
            url = response.url
            if ("google.com/maps" in url and any(x in url for x in ["search", "preview", "vt/pb"])) or "googleusercontent.com" in url:
                body = await response.body()
                chunk = {
                    "url": url,
                    "status": response.status,
                    "body": body.hex() 
                }
                self.raw_responses.append(chunk)
                
                # DEBUG: Always save the very first chunk for inspection
                if len(self.raw_responses) == 1:
                    with open("/app/data/sample_chunk.hex", "w") as f:
                        f.write(body.hex())
                    self.logger.info("DEBUG: Saved initial sample data chunk.")
        except:
            pass

    async def _block_media(self, route: Route):
        if route.request.resource_type in ["image", "font", "media", "stylesheet"]:
            await route.abort()
        else:
            await route.continue_()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def scrape(self, query: str, zoom_level: str = "fastest") -> List[Dict[str, Any]]:
        self.raw_responses = []
        self.logger.info(f"Navigating to query: {query}")

        engine = self.factory.create_engine()
        await engine.launch()
        
        try:
            page = await engine.get_page()
            
            # Simple User Agent setting
            await page.set_extra_http_headers({
                "User-Agent": self.stealth.get_random_user_agent()
            })
            
            # Set up Interception & Resource Blocking
            await page.route("**/*", self._block_media)
            page.on("response", self._intercept_response)

            search_url = f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"
            await page.goto(search_url, wait_until="domcontentloaded")
            
            # Wait for content to stream in
            await asyncio.sleep(5)

            # Simulation of interaction (Scrolls)
            for i in range(8): 
                await page.mouse.wheel(0, 4000)
                await asyncio.sleep(2)
            
            # Final wait to ensure all intercepted responses are processed
            await asyncio.sleep(3)
            
            self.logger.info(f"Scraping completed. Captured {len(self.raw_responses)} chunks.")
            results = self.parser.parse_raw_responses(self.raw_responses)
            return results
            
        finally:
            await engine.close()

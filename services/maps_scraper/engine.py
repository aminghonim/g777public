from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Browser, Page, Playwright
import yaml
import logging
from typing import Optional

class AbstractBrowserEngine(ABC):
    """
    Abstract base class for browser engines (Strategy Pattern).
    Ensures a consistent interface for Chromium and Lightpanda.
    """
    
    @abstractmethod
    async def launch(self) -> None:
        """Launches the browser instance."""
        pass

    @abstractmethod
    async def get_page(self) -> Page:
        """Creates and returns a new page instance."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Closes the browser and stops the automation engine."""
        pass

class ChromiumEngine(AbstractBrowserEngine):
    """
    Stable engine implementation using Playwright's native Chromium.
    Used for Phase 1 production-ready scraping.
    """
    
    def __init__(self, headless: bool = True):
        self.headless: bool = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None

    async def launch(self) -> None:
        """Starts Playwright and launches Chromium."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        if not self.browser:
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
        logging.info("Chromium Engine launched successfully.")

    async def get_page(self) -> Page:
        """Ensures browser is launched and returns a new page."""
        if not self.browser:
            await self.launch()
        return await self.browser.new_page()

    async def close(self) -> None:
        """Gracefully closes browser and playwright."""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        logging.info("Chromium Engine shutdown.")

class LightpandaEngine(AbstractBrowserEngine):
    """
    R&D engine implementation using Lightpanda (CDP over WebSocket).
    Designed for high-efficiency, low-RAM environments.
    """
    
    def __init__(self, ws_url: str):
        self.ws_url: str = ws_url
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None

    async def launch(self) -> None:
        """Connects to Lightpanda instance via CDP."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        if not self.browser:
            # Lightpanda is compatible with Chrome DevTools Protocol
            self.browser = await self.playwright.chromium.connect_over_cdp(self.ws_url)
        logging.info(f"Connected to Lightpanda Engine at {self.ws_url}")

    async def get_page(self) -> Page:
        """Returns a new page from the Lightpanda connection."""
        if not self.browser:
            await self.launch()
        return await self.browser.new_page()

    async def close(self) -> None:
        """Closes the connection."""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        logging.info("Lightpanda Engine disconnected.")

class BrowserFactory:
    """
    Factory to instantiate the appropriate browser engine based on configuration.
    Follows the Config-First and Modular Integrity principles.
    """
    
    def __init__(self, config_path: str = "config/maps_scraper.yaml"):
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Failed to load engine config: {e}")
            self.config = {}

    def create_engine(self) -> AbstractBrowserEngine:
        """
        Creates an engine instance based on 'browser.engine' setting.
        
        Returns:
            An instance of AbstractBrowserEngine.
        """
        browser_cfg = self.config.get('browser', {})
        engine_type = browser_cfg.get('engine', 'chromium').lower()
        headless = browser_cfg.get('headless', True)
        
        if engine_type == "chromium":
            logging.info("Factory: Creating ChromiumEngine")
            return ChromiumEngine(headless=headless)
        elif engine_type == "lightpanda":
            ws_url = browser_cfg.get('lightpanda_ws_url')
            if not ws_url:
                raise ValueError("lightpanda_ws_url is required for lightpanda engine")
            logging.info("Factory: Creating LightpandaEngine")
            return LightpandaEngine(ws_url=ws_url)
        else:
            raise ValueError(f"Unknown browser engine type: {engine_type}")

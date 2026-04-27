"""
Google Maps Extractor — Hybrid Scraping Module.

Extraction pipeline:
    Layer 1 (Fast/Free):  ScraplingEngine.stealth_fetch() with CSS selectors.
    Layer 2 (AI Heal):    ScraplingEngine.execute_smart_action() with browser-use
                          agent when selectors fail repeatedly.
    Layer 3 (Legacy):     undetected-chromedriver Selenium fallback for
                          environments where Scrapling/browser-use are unavailable.

Output: JSON file in data/ directory with business listings.
"""

import asyncio
import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

from backend.core.event_broker import event_broker

logger = logging.getLogger(__name__)


class MapsExtractor:
    """
    Google Maps Scraper with Self-Healing AI fallback.

    Extracts: Name, Phone, Website, Address, Rating.

    Strategy:
        1. Try ScraplingEngine first (fast, free, adaptive CSS selectors).
        2. If selectors fail >= threshold times, trigger AI Self-Healing
           via browser-use (ScraplingEngine.execute_smart_action).
        3. If ScraplingEngine is unavailable, fall back to legacy
           undetected-chromedriver Selenium path.
    """

    # CSS selectors for Google Maps result items
    _FEED_SELECTOR: str = "div[role='feed']"
    _ARTICLE_SELECTOR: str = "div[role='article']"

    def __init__(self, headless: bool = True) -> None:
        self.headless: bool = headless
        self.driver: Optional[Any] = None
        self._engine: Optional[Any] = None

    def _get_engine(self) -> Optional[Any]:
        """Lazy-load ScraplingEngine to avoid circular imports."""
        if self._engine is None:
            try:
                from backend.scrapling_engine import ScraplingEngine

                self._engine = ScraplingEngine()
            except Exception as engine_err:
                logger.warning(
                    "ScraplingEngine unavailable, will use legacy Selenium: %s",
                    engine_err,
                )
        return self._engine

    async def scrape(
        self,
        query: str,
        limit: int = 50,
        scrolling_depth: int = 2,
    ) -> Dict[str, Any]:
        """
        Main entry point for Maps scraping.

        Attempts the ScraplingEngine hybrid path first. Falls back to
        the legacy Selenium path if the engine is not available.

        Args:
            query: Search term (e.g. 'restaurants in Cairo').
            limit: Maximum number of results to extract.
            scrolling_depth: Number of scroll iterations for lazy-loaded results.

        Returns:
            Dict with source, keyword, timestamp, and results list.
        """
        user_id = "global"
        engine = self._get_engine()

        await event_broker.publish_log(
            f"Starting Maps Scraping for: {query} (Depth: {scrolling_depth})",
            user_id=user_id,
        )

        # Decide execution path based on engine availability
        if engine and engine.is_available:
            results = await self._scrape_with_engine(
                engine, query, limit, scrolling_depth, user_id
            )
        else:
            results = await self._scrape_with_selenium(
                query, limit, scrolling_depth, user_id
            )

        return self._save_results(query, results)

    # ------------------------------------------------------------------ #
    #  Path 1: ScraplingEngine + AI Self-Healing
    # ------------------------------------------------------------------ #

    async def _scrape_with_engine(
        self,
        engine: Any,
        query: str,
        limit: int,
        scrolling_depth: int,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Scrape Google Maps using ScraplingEngine.

        Uses execute_smart_action which internally handles:
            - Adaptive CSS selectors (Layer 1)
            - AI Self-Healing via browser-use (Layer 2)
        """
        url = f"https://www.google.com/maps/search/{query}"
        ai_task = (
            f"Navigate to Google Maps, search for '{query}', "
            f"scroll through results {scrolling_depth} times, "
            f"and extract all business names, phone numbers, "
            f"addresses, and ratings from the listings."
        )

        await event_broker.publish_log(
            f"Using ScraplingEngine hybrid path for: {query}",
            user_id=user_id,
        )

        raw_results = await engine.execute_smart_action(
            url=url,
            action=ai_task,
            selector=self._ARTICLE_SELECTOR,
        )

        # Normalize results into standard format
        results: List[Dict[str, Any]] = []
        if not raw_results:
            return results

        for idx, item in enumerate(raw_results[:limit]):
            try:
                data = self._parse_item(item)
                if data:
                    results.append(data)

                if (idx + 1) % 5 == 0:
                    await event_broker.publish_log(
                        f"Extracted {idx + 1}/{min(len(raw_results), limit)} "
                        f"businesses...",
                        user_id=user_id,
                    )
            except Exception as parse_err:
                logger.warning("Error parsing Maps item: %s", parse_err)

        return results

    # ------------------------------------------------------------------ #
    #  Path 2: Legacy Selenium (undetected-chromedriver)
    # ------------------------------------------------------------------ #

    def _init_driver(self) -> None:
        """Initialize undetected Chrome driver with bypass settings."""
        if self.driver:
            return

        import undetected_chromedriver as uc

        options = uc.ChromeOptions()
        options.add_argument("--window-position=-32000,-32000")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=en")

        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        options.add_argument(f"--user-agent={user_agent}")

        try:
            self.driver = uc.Chrome(options=options, use_subprocess=True)
        except Exception as driver_err:
            logger.error(
                "Failed to init undetected_chromedriver for Maps: %s",
                driver_err,
            )
            raise

    async def _scrape_with_selenium(
        self,
        query: str,
        limit: int,
        scrolling_depth: int,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Legacy Selenium scraping path.

        Used when ScraplingEngine is unavailable or explicitly disabled.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        self._init_driver()
        results: List[Dict[str, Any]] = []

        try:
            # Referrer trick to avoid direct navigation detection
            logger.info(
                "Initializing Maps session via Wikipedia (Referrer Trick)..."
            )
            self.driver.get("https://www.wikipedia.org")
            await asyncio.sleep(2)

            url = f"https://www.google.com/maps/search/{query}"
            self.driver.get(url)
            logger.info("Navigated to Maps: %s", query)
            await event_broker.publish_log(
                f"Maps Loaded (Selenium): {query}",
                user_id=user_id,
            )

            # Scroll to load more results
            for step in range(scrolling_depth):
                await event_broker.publish_log(
                    f"Scrolling maps results... "
                    f"Step {step + 1}/{scrolling_depth}",
                    user_id=user_id,
                )
                try:
                    wait = WebDriverWait(self.driver, 10)
                    scroll_container = wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, self._FEED_SELECTOR)
                        )
                    )
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight",
                        scroll_container,
                    )
                    await asyncio.sleep(2)
                except Exception as scroll_err:
                    logger.warning(
                        "Scrolling error (might be at end): %s", scroll_err
                    )
                    break

            # Extract visible items
            items = self.driver.find_elements(
                By.CSS_SELECTOR, self._ARTICLE_SELECTOR
            )
            total_found = len(items)
            await event_broker.publish_log(
                f"Found {total_found} listings. Extracting details...",
                user_id=user_id,
            )

            for idx, item in enumerate(items[:limit]):
                try:
                    text_content = item.text
                    data = self._parse_text(text_content)
                    if data:
                        results.append(data)

                    if (idx + 1) % 5 == 0:
                        await event_broker.publish_log(
                            f"Extracted {idx + 1}/"
                            f"{min(total_found, limit)} businesses...",
                            user_id=user_id,
                        )
                except Exception as item_err:
                    logger.warning("Error parsing item: %s", item_err)

        except Exception as scrape_err:
            logger.error("Selenium scrape failed: %s", scrape_err)
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None

        return results

    # ------------------------------------------------------------------ #
    #  Parsing Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_item(item: Any) -> Optional[Dict[str, Any]]:
        """
        Parse a Scrapling element into a normalized business dict.

        Args:
            item: A Scrapling element or browser-use result object.

        Returns:
            Dict with name, phone, full_text or None if unparseable.
        """
        try:
            text_content = ""
            # Scrapling Selector elements have get_all_text() which
            # recursively extracts text from all children — essential
            # for nested elements like Google Maps article divs where
            # .text only returns direct (often empty) text.
            if hasattr(item, "get_all_text"):
                text_content = item.get_all_text(separator="\n", strip=True) or ""
            elif hasattr(item, "get_text"):
                text_content = item.get_text(strip=True) or ""
            elif hasattr(item, "text"):
                text_content = item.text or ""
            elif isinstance(item, str):
                text_content = item
            elif isinstance(item, dict):
                text_content = item.get("text", str(item))

            if not text_content:
                return None

            return MapsExtractor._parse_text(text_content)
        except (AttributeError, TypeError) as parse_err:
            logger.warning("Parse item error: %s", parse_err)
            return None

    @staticmethod
    def _parse_text(text_content: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from raw text content.

        Args:
            text_content: Raw text from a Maps listing element.

        Returns:
            Dict with name, phone, full_text or None.
        """
        if not text_content or not text_content.strip():
            return None

        lines = text_content.split("\n")
        data: Dict[str, Any] = {}

        if lines:
            data["name"] = lines[0].strip()

        phone_match = re.search(
            r"(\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?"
            r"\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})",
            text_content,
        )
        data["phone"] = (
            phone_match.group(1).strip() if phone_match else None
        )

        data["full_text"] = text_content
        return data

    # ------------------------------------------------------------------ #
    #  Output
    # ------------------------------------------------------------------ #

    @staticmethod
    def _save_results(
        query: str, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Persist results to a timestamped JSON file in data/.

        Args:
            query: The original search query.
            results: List of extracted business dicts.

        Returns:
            The full output dict (source, keyword, timestamp, results).
        """
        timestamp = int(time.time())
        filename = f"data/maps_results_{timestamp}.json"
        os.makedirs("data", exist_ok=True)

        output: Dict[str, Any] = {
            "source": "google_maps",
            "keyword": query,
            "timestamp": timestamp,
            "results": results,
        }

        with open(filename, "w", encoding="utf-8") as output_file:
            json.dump(output, output_file, ensure_ascii=False, indent=2)

        return output

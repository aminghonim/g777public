import logging
import json
import time
import os
import re
from typing import List, Dict
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.core.event_broker import event_broker
import asyncio

logger = logging.getLogger(__name__)


class MapsExtractor:
    """
    Google Maps Scraper using Selenium (Undetected Headless).
    Extracts: Name, Phone, Website, Address, Rating.
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """Initializes the undetected Chrome driver with Bypass Hack."""
        if not self.driver:
            options = uc.ChromeOptions()

            # BYPASS HACK: Run visible but off-screen to avoid Headless detection
            options.add_argument("--window-position=-32000,-32000")
            options.add_argument("--window-size=1920,1080")

            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--lang=en")

            # Hardcoded realistic User-Agent
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            options.add_argument(f"--user-agent={user_agent}")

            try:
                self.driver = uc.Chrome(options=options, use_subprocess=True)
            except Exception as e:
                logger.error("Failed to init undetected_chromedriver for Maps: %s", e)
                raise

    async def scrape(
        self, query: str, limit: int = 50, scrolling_depth: int = 2
    ) -> Dict[str, any]:
        self._init_driver()
        results = []
        user_id = "global"  # Could be passed from caller

        await event_broker.publish_log(
            f"Starting Maps Scraping for: {query} (Depth: {scrolling_depth})",
            user_id=user_id,
        )

        try:
            # Step 0: Referrer Trick - Navigate to neutral site
            logger.info("Initializing Maps session via Wikipedia (Referrer Trick)...")
            self.driver.get("https://www.wikipedia.org")
            await asyncio.sleep(2)

            url = f"https://www.google.com/maps/search/{query}"
            self.driver.get(url)
            logger.info(f"Navigated to Maps: {query}")
            await event_broker.publish_log(f"Maps Loaded: {query}", user_id=user_id)

            # --- GAP 3: Scrolling Logic to load more results ---
            scroll_container_selector = "div[role='feed']"

            for d in range(scrolling_depth):
                await event_broker.publish_log(
                    f"Scrolling maps results... Step {d+1}/{scrolling_depth}",
                    user_id=user_id,
                )
                try:
                    # Find the scrollable container (results feed)
                    wait = WebDriverWait(self.driver, 10)
                    scroll_container = wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, scroll_container_selector)
                        )
                    )

                    # Execute JS Scroll
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight",
                        scroll_container,
                    )
                    await asyncio.sleep(2)  # Wait for "Load More" to trigger
                except Exception as e:
                    logger.warning(f"Scrolling error (might be at end of list): {e}")
                    break

            # Find all visible items
            items = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            total_found = len(items)
            await event_broker.publish_log(
                f"Found {total_found} listings. Extracting details...", user_id=user_id
            )

            for idx, item in enumerate(items[:limit]):
                try:
                    data = {}
                    text_content = item.text
                    lines = text_content.split("\n")
                    if len(lines) > 0:
                        data["name"] = lines[0]

                    # Phone Regex
                    phone_match = re.search(
                        r"(\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})",
                        text_content,
                    )
                    data["phone"] = (
                        phone_match.group(1).strip() if phone_match else None
                    )

                    data["full_text"] = text_content
                    results.append(data)

                    if (idx + 1) % 5 == 0:
                        await event_broker.publish_log(
                            f"Extracted {idx+1}/{min(total_found, limit)} businesses...",
                            user_id=user_id,
                        )
                except Exception as e:
                    logger.warning(f"Error parsing item: {e}")

        except Exception as e:
            logger.error(f"Scrape failed: {e}")
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    # Suppress WinError 6 and other noisy shutdown errors
                    pass
                self.driver = None

        # Save to JSON
        timestamp = int(time.time())
        filename = f"data/maps_results_{timestamp}.json"
        os.makedirs("data", exist_ok=True)

        output = {
            "source": "google_maps",
            "keyword": query,
            "timestamp": timestamp,
            "results": results,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        return output

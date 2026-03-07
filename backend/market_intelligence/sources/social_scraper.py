import logging
import json
import time
import os
import random
import re
import urllib.parse
from typing import Dict, List
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from backend.core.event_broker import event_broker
import asyncio

logger = logging.getLogger(__name__)


class SocialScraper:
    """
    Social Media Scraper using Google Dorking.
    Extracts: Phone, Email from description snippets.
    """

    def __init__(self, headless: bool = True):
        """Initialize the SocialScraper with undetected-chromedriver."""
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

            # Hardcoded realistic User-Agent
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            options.add_argument(f"--user-agent={user_agent}")

            try:
                self.driver = uc.Chrome(options=options, use_subprocess=True)
            except Exception as e:
                logger.error("Failed to init undetected_chromedriver: %s", e)
                raise

    async def scrape(
        self, keyword: str, limit: int = 20, scrolling_depth: int = 2
    ) -> Dict[str, any]:
        """
        Scrape social profiles using Google Dorking with Pagination (Depth).
        """
        results = []
        user_id = "global"

        await event_broker.publish_log(
            f"Starting Social Dorking for: {keyword} (Depth: {scrolling_depth})",
            user_id=user_id,
        )

        try:
            self._init_driver()

            # Construct a powerful Dork query
            dorks = "site:facebook.com OR site:linkedin.com OR site:instagram.com"
            phone_identifiers = '("+20" OR "010" OR "011" OR "012" OR "015")'
            query = f'{dorks} "{keyword}" AND {phone_identifiers}'
            encoded_query = urllib.parse.quote(query)

            # Step 0: Referrer Trick
            logger.info("Initializing session via Wikipedia (Referrer Trick)...")
            self.driver.get("https://www.wikipedia.org")
            await asyncio.sleep(2)

            # --- GAP 3: Multi-page Dorking (Pagination) ---
            for page in range(scrolling_depth):
                if len(results) >= limit:
                    break

                p_url = (
                    f"https://www.google.com/search?q={encoded_query}&start={page * 10}"
                )
                await event_broker.publish_log(
                    f"Fetching search results page {page + 1}...", user_id=user_id
                )
                self.driver.get(p_url)
                await asyncio.sleep(random.uniform(4, 6))

                page_source = self.driver.page_source.lower()
                if "captcha" in page_source or "not a robot" in page_source:
                    await event_broker.publish_log(
                        "Blocked by Google CAPTCHA. Stopping.", user_id=user_id
                    )
                    break

                result_containers = self.driver.find_elements(
                    By.CSS_SELECTOR, "div.g, div.yuRUbf, div.tF2Cxc"
                )
                logger.info(
                    "Page %d: Found %d containers", page + 1, len(result_containers)
                )

                for item in result_containers:
                    if len(results) >= limit:
                        break
                    try:
                        full_text = item.text
                        try:
                            anchor = item.find_element(By.CSS_SELECTOR, "a")
                            url = anchor.get_attribute("href")
                            title = anchor.text or "No Title"
                        except:
                            url = None
                            title = "No Link"

                        # Egyptian phone regex
                        cleaned_text = re.sub(r"[\s\-\(\)]", "", full_text)
                        phone_pattern = r"(\+201[0125]\d{8}|01[0125]\d{8})"
                        phones = re.findall(phone_pattern, cleaned_text)

                        if url and any(
                            domain in url
                            for domain in [
                                "facebook.com",
                                "linkedin.com",
                                "instagram.com",
                            ]
                        ):
                            data = {
                                "url": url,
                                "title": title,
                                "contacts": (
                                    ", ".join(phones) if phones else "Check Description"
                                ),
                                "phone": phones[0] if phones else None,
                                "snippet": full_text[:200].replace("\n", " "),
                            }
                            results.append(data)
                            await event_broker.publish_log(
                                f"Extracted lead: {title}", user_id=user_id
                            )
                    except Exception as inner_e:
                        continue

                # Check for next page button
                try:
                    next_button = self.driver.find_elements(By.ID, "pnnext")
                    if not next_button:
                        await event_broker.publish_log(
                            "No more pages found.", user_id=user_id
                        )
                        break
                    await asyncio.sleep(random.uniform(2, 3))
                except:
                    break

            logger.info("Total social leads extracted: %d", len(results))

            if not results and len(result_containers) > 0:
                logger.warning(
                    "Found containers but no results matched the social domain filtering."
                )

        except Exception as e:
            logger.error("Social Scrape (Selenium) failed: %s", e)
            return {"success": False, "error": str(e), "results": []}
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
        filename = f"data/social_results_{timestamp}.json"
        os.makedirs("data", exist_ok=True)

        output = {
            "success": True,
            "source": "social_media",
            "keyword": keyword,
            "timestamp": timestamp,
            "results": results,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        return output

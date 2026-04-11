"""
WhatsApp Group Finder - FACEBOOK HUNTER EDITION (Selenium Based)
Method: Real Browser Automation (Undetected Chrome)
Target: Facebook Public Posts & Groups via Google Cache
Features: Deep Hunt + Live Verification + Anti-Ban Delays + Auto-Healing
"""

import time
import re
import random
import requests
import os
import sys
import logging
from typing import List, Set, Optional
from urllib.parse import unquote

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

# ENSURE CONFIG IS LOADED
try:
    from core.config import settings
except ImportError:
    # Fallback for direct script execution
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from core.config import settings

try:
    from .browser_core import WhatsAppBrowser
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from backend.browser_core import WhatsAppBrowser

# Initialize logger
logger = logging.getLogger(__name__)

class GroupFinder:
    """
    WhatsApp Group Finder - FACEBOOK HUNTER EDITION
    Provides specialized hunting for WhatsApp groups on Facebook using Selenium.
    """
    def __init__(self):
        self.driver = None
        self.found_links: Set[str] = set()
        self.session = requests.Session()
        # Securely managed User-Agent or default
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _ensure_driver(self) -> None:
        """Ensure the browser is running and responsive."""
        if self.driver:
            try:
                # Check if alive
                self.driver.current_url
                return
            except Exception:
                logger.warning("Browser disconnected. Restarting...")
                self.driver = None

        logger.info("[System] Launching Hunter Browser...")
        try:
            browser = WhatsAppBrowser(headless=False) 
            self.driver = browser.initialize_driver()
        except Exception as e:
            logger.error("Failed to launch browser: %s", e)
            raise

    def extract_links_from_text(self, text: str) -> List[str]:
        """Powerful Regex for all WhatsApp Link formats"""
        if not text:
            return []
        
        found = set()
        patterns = [
            r'chat\.whatsapp\.com/[A-Za-z0-9]{20,}',
            r'whatsapp\.com/channel/[A-Za-z0-9]{20,}',
            r'wa\.me/[0-9]+',
        ]
        
        for pat in patterns:
            matches = re.findall(pat, text)
            for m in matches:
                # Sanitize
                clean = m.split('"')[0].split("'")[0].split('<')[0].strip()
                if not clean.startswith('http'):
                    link = f"https://{clean}"
                else:
                    link = clean
                found.add(link)
        
        return list(found)

    def search_via_browser(self, keyword: str, country: str = "") -> List[str]:
        """Uses the real browser to search Google > Facebook"""
        self._ensure_driver()
        
        search_term = f'site:facebook.com "chat.whatsapp.com" {keyword} {country}'
        logger.info("🕵️‍♂️ [Hunter] Hunting for: %s...", keyword)
        
        new_links = []
        
        try:
            # 1. Go to Google
            self.driver.get("https://www.google.com")
            time.sleep(random.uniform(2, 4))
            
            # 2. Type Query (Multi-Selector)
            search_box = None
            selectors = ["textarea[name='q']", "input[name='q']", "input[type='text']", "input[aria-label='Search']"]
            
            for selector in selectors:
                try:
                    el = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if el.is_displayed() and el.is_enabled():
                        search_box = el
                        logger.debug("Found search box: %s", selector)
                        break
                except Exception:
                    continue
                
            if not search_box:
                try:
                    search_box = self.driver.switch_to.active_element
                    logger.debug("Using active element as search box")
                except Exception:
                    logger.warning("Search box not found. Skipping...")
                    return []

            search_box.clear()
            search_box.send_keys(search_term)
            time.sleep(1)
            search_box.send_keys(Keys.RETURN)
            
            # 3. Process Pages
            max_pages = 2
            for page in range(max_pages):
                logger.info("Scanning Page %d/%d...", page + 1, max_pages)
                
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "search"))
                    )
                except Exception:
                    logger.warning("Timeout waiting for results.")
                    break
                
                # A. Scrape Visible Links
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    links_in_snippets = self.extract_links_from_text(body_text)
                    
                    for link in links_in_snippets:
                        if link not in self.found_links:
                            self.found_links.add(link)
                            new_links.append(link)
                            logger.info("Snippet found: %s...", link[:40])
                except Exception:
                    pass

                # B. DEEP HUNT
                logger.info("🕷️ Starting Deep Hunt...")
                try:
                    fb_links_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'facebook.com') and not(contains(@href, 'google'))]")
                    fb_urls = []
                    for el in fb_links_elements:
                        url = el.get_attribute("href")
                        if url:
                            fb_urls.append(url)
                    
                    fb_urls = list(dict.fromkeys(fb_urls))
                    logger.info("🎯 Found %d potential Facebook pages.", len(fb_urls))
                    
                    original_window = self.driver.current_window_handle
                    
                    for i, fb_url in enumerate(fb_urls):
                        try:
                            self.driver.execute_script("window.open('');")
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            self.driver.get(fb_url)
                            
                            time.sleep(random.uniform(3, 6)) 
                            
                            page_content = self.driver.find_element(By.TAG_NAME, "body").text
                            deep_links = self.extract_links_from_text(page_content)
                            
                            found_here = 0
                            for dl in deep_links:
                                if dl not in self.found_links:
                                    self.found_links.add(dl)
                                    new_links.append(dl)
                                    found_here += 1
                            
                            if found_here > 0:
                                logger.info("💎 Deep Hunt [%d]: Found %d links!", i + 1, found_here)
                            
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                            
                        except Exception:
                            try:
                                if len(self.driver.window_handles) > 1:
                                    self.driver.close()
                                self.driver.switch_to.window(original_window)
                            except Exception:
                                pass

                except Exception as e:
                    logger.error("Deep Hunt Loop Error: %s", e)

                # C. Next Page
                try:
                    next_btn = self.driver.find_elements(By.ID, "pnnext")
                    if next_btn:
                        next_btn[0].click()
                        delay = random.uniform(8, 12)
                        logger.info("Waiting %.1fs for Google...", delay)
                        time.sleep(delay)
                    else:
                        logger.info("⏹️ No more pages.")
                        break
                except Exception:
                    break
                    
        except Exception as e:
            logger.error("Search Error: %s", e)
            
        return new_links

    def check_link_validity(self, link: str) -> bool:
        """Fast validity check"""
        try:
            resp = self.session.head(link, timeout=5, allow_redirects=True)
            return resp.status_code != 404
        except Exception:
            return True

    def filter_valid_links(self, links: List[str]) -> List[str]:
        """Validate a list of links"""
        if not links:
            return []
        
        logger.info("🔍 Validating %d links...", len(links))
        valid = []
        for i, link in enumerate(links, 1):
            if self.check_link_validity(link):
                valid.append(link)
            time.sleep(0.1)
            
        logger.info("Final Validated: %d groups.", len(valid))
        return valid

    def find_groups(self, keywords: List[str], country: str = "") -> List[str]:
        """Main Entry Point"""
        if isinstance(keywords, str):
            keywords = [keywords]
        
        logger.info("="*60)
        logger.info("FACEBOOK GROUP HUNTER (Resource Managed)")
        logger.info("="*60)
        
        all_results = []
        try:
            for kw in keywords:
                res = self.search_via_browser(kw, country)
                all_results.extend(res)
                time.sleep(2)

            unique_links = list(set(all_results))
            logger.info("🎯 Total Raw Links: %d", len(unique_links))
            
            final_links = self.filter_valid_links(unique_links)
            return final_links
        finally:
            if self.driver:
                logger.info("Closing browser resources...")
                self.driver.quit()
                self.driver = None
        
    def save(self, links: List[str]) -> None:
        """Save found links to the configured file."""
        if not links:
            return
        
        data_dir = settings.system.data_dir
        filename = f"facebook_groups_{int(time.time())}.txt"
        filepath = os.path.join(data_dir, filename)
        
        os.makedirs(data_dir, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            for l in links:
                f.write(l + "\n")
        logger.info("💾 Saved to %s", filepath)

if __name__ == "__main__":
    # Test session
    logging.basicConfig(level=logging.INFO)
    finder = GroupFinder()
    try:
        links = finder.find_groups(["ملابس جملة", "مكتب ملابس"], country="القاهرة")
        finder.save(links)
    except Exception as e:
        logger.error("Main Execution Error: %s", e)
    finder = GroupFinder()
    links = finder.find_groups(["ملابس جملة", "مكتب ملابس"], country="القاهرة")
    finder.save(links)


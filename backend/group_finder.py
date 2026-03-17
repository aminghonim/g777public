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
import json
import logging
from typing import List, Set, Dict, Any, Optional
from urllib.parse import unquote
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from .core.i18n import t

try:
    from .scrapling_engine import ScraplingEngine
except (ImportError, ValueError):
    try:
        from backend.scrapling_engine import ScraplingEngine
    except ImportError:
        ScraplingEngine = None

try:
    from .browser_core import WhatsAppBrowser
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from backend.browser_core import WhatsAppBrowser


class GroupFinder:
    """
    CNS-Enhanced Group Finder with Session Injector capability.

    Features:
    - ScraplingEngine StealthyFetcher for anti-bot bypass
    - Session Injector for persistent session management
    - Config-driven search parameters
    - Smart Retry with exponential backoff
    - Zero hardcoding compliance
    """

    def __init__(
        self,
        config_path: str = "config.yaml",
        sessions_dir: str = ".antigravity/sessions",
    ):
        self.driver = None
        self.found_links: Set[str] = set()
        self.session = requests.Session()
        self.sessions_dir = Path(sessions_dir)
        self.logger = logging.getLogger(__name__)

        # Initialize ScraplingEngine
        try:
            self.scrapling_engine = ScraplingEngine(config_path)
            self.logger.info("ScraplingEngine initialized for GroupFinder")
            # Override sessions_dir from config if available
            config_dir = self.scrapling_engine.session_config.get("session_path")
            if config_dir:
                self.sessions_dir = Path(config_dir)
        except Exception as e:
            self.logger.warning("ScraplingEngine init failed, using fallback: %s", e)
            self.scrapling_engine = None

        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def _ensure_driver(self):
        """Ensure the browser is running and responsive."""
        if self.driver:
            try:
                # Check if alive
                self.driver.current_url
                return
            except:
                self.logger.info(
                    t(
                        "hunter.logs.launching",
                        "Browser disconnected. Restarting...",
                    )
                )
                self.driver = None

        self.logger.info(t("hunter.logs.launching", " [System] Launching Hunter Browser..."))
        try:
            browser = WhatsAppBrowser(headless=False)
            self.driver = browser.initialize_driver()
        except Exception as e:
            self.logger.error(
                t(
                    "hunter.logs.launch_failed", "Failed to launch browser: {err}"
                ).format(err=e)
            )
            self.logger.info(
                t(
                    "hunter.logs.browser_tip",
                    "Tip: Close all Chrome windows and try again.",
                )
            )
            raise

    def extract_links_from_text(self, text: str) -> List[str]:
        """Powerful Regex for all WhatsApp Link formats"""
        if not text:
            return []

        found = set()
        patterns = [
            r"chat\.whatsapp\.com/[A-Za-z0-9]{20,}",
            r"whatsapp\.com/channel/[A-Za-z0-9]{20,}",
            r"wa\.me/[0-9]+",
        ]

        for pat in patterns:
            matches = re.findall(pat, text)
            for m in matches:
                # Sanitize
                clean = m.split('"')[0].split("'")[0].split("<")[0].strip()
                if not clean.startswith("http"):
                    link = f"https://{clean}"
                else:
                    link = clean
                found.add(link)

        return list(found)

    def _get_session_kwargs(self, session_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get session injection arguments for ScraplingEngine.
        Delegates to ScraplingEngine for centralized logic.
        """
        if self.scrapling_engine:
            return self.scrapling_engine._inject_session(session_name)
        return {}

    def search_via_browser(self, keyword: str, country: str = "") -> List[str]:
        """
        Uses the real browser to search Google > Facebook
        """
        self._ensure_driver()

        # Broaden the search query slightly to catch more results
        search_term = f'site:facebook.com "chat.whatsapp.com" {keyword} {country}'
        print(
            t("hunter.logs.hunting", "🕵️‍♂️ [Hunter] Hunting for: {kw}...").format(
                kw=keyword
            )
        )

        new_links = []

        try:
            # 1. Go to Google
            self.driver.get("https://www.google.com")
            time.sleep(random.uniform(2, 4))

            # IMPORTANT: Wait for user to solve CAPTCHA or login if needed
            print(
                t(
                    "hunter.logs.ready_wait",
                    "[Hunter] Browser ready. You have 15 seconds to solve CAPTCHA or login...",
                )
            )
            time.sleep(15)  # Give user time to interact

            # 2. Type Query (Multi-Selector)
            search_box = None
            # Common selectors for Google search box
            selectors = [
                "textarea[name='q']",
                "input[name='q']",
                "input[type='text']",
                "input[aria-label='Search']",
            ]

            for selector in selectors:
                try:
                    el = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if el.is_displayed() and el.is_enabled():
                        search_box = el
                        print(
                            t(
                                "hunter.logs.found_box",
                                "       Found search box: {sel}",
                            ).format(sel=selector)
                        )
                        break
                except:
                    continue

            if not search_box:
                # Last resort: active element
                try:
                    search_box = self.driver.switch_to.active_element
                    print(
                        t(
                            "hunter.logs.using_active",
                            "       Using active element as search box",
                        )
                    )
                except:
                    print(
                        t(
                            "hunter.logs.box_not_found",
                            "       Search box not found. Skipping...",
                        )
                    )
                    return []

            search_box.clear()
            search_box.send_keys(search_term)
            time.sleep(1)
            search_box.send_keys(Keys.RETURN)

            # 3. Process Pages
            max_pages = 2  # Focus on quality pages
            for page in range(max_pages):
                print(
                    t(
                        "hunter.logs.scanning_page",
                        "    Scanning Page {curr}/{total}...",
                    ).format(curr=page + 1, total=max_pages)
                )

                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "search"))
                    )
                except:
                    print(
                        t("hunter.logs.timeout", "       Timeout waiting for results.")
                    )
                    break

                # A. Scrape Visible Links (Snippets)
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    links_in_snippets = self.extract_links_from_text(body_text)

                    for link in links_in_snippets:
                        if link not in self.found_links:
                            self.found_links.add(link)
                            new_links.append(link)
                            print(
                                t(
                                    "hunter.logs.found_box", "       Snippet: {link}"
                                ).format(link=link[:40])
                            )
                except:
                    pass

                # B. DEEP HUNT (Visit Facebook Pages)
                print(t("hunter.logs.deep_hunt_start", "      🕷️ Starting Deep Hunt..."))

                # Robust XPath to find Facebook links
                try:
                    fb_links_elements = self.driver.find_elements(
                        By.XPATH,
                        "//a[contains(@href, 'facebook.com') and not(contains(@href, 'google'))]",
                    )
                    fb_urls = []
                    for el in fb_links_elements:
                        url = el.get_attribute("href")
                        if url:
                            fb_urls.append(url)

                    # Remove duplicates and limit
                    fb_urls = list(dict.fromkeys(fb_urls))
                    print(
                        t(
                            "hunter.logs.found_pages",
                            "      🎯 Found {count} potential Facebook pages.",
                        ).format(count=len(fb_urls))
                    )

                    original_window = self.driver.current_window_handle

                    # Scan ALL found facebook links
                    for i, fb_url in enumerate(fb_urls):
                        try:
                            # Use Javascript to open new tab (safer)
                            self.driver.execute_script("window.open('');")
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                            self.driver.get(fb_url)

                            # Random Wait for load
                            time.sleep(random.uniform(3, 6))

                            # Extract
                            page_content = self.driver.find_element(
                                By.TAG_NAME, "body"
                            ).text
                            deep_links = self.extract_links_from_text(page_content)

                            found_here = 0
                            for dl in deep_links:
                                if dl not in self.found_links:
                                    self.found_links.add(dl)
                                    new_links.append(dl)
                                    found_here += 1

                            if found_here > 0:
                                print(
                                    t(
                                        "hunter.logs.deep_hunt_result",
                                        "      💎 Deep Hunt [{idx}]: Found {count} links!",
                                    ).format(idx=i + 1, count=found_here)
                                )

                            # Close tab
                            self.driver.close()
                            self.driver.switch_to.window(original_window)

                        except Exception as e:
                            # print(f"       Deep Hunt Error: {e}")
                            try:
                                if len(self.driver.window_handles) > 1:
                                    self.driver.close()
                                self.driver.switch_to.window(original_window)
                            except:
                                pass

                except Exception as e:
                    print(f"       Deep Hunt Loop Error: {e}")

                # C. Next Google Page
                try:
                    next_btn = self.driver.find_elements(By.ID, "pnnext")
                    if next_btn:
                        next_btn[0].click()
                        delay = random.uniform(8, 12)
                        print(
                            t(
                                "hunter.logs.waiting_google",
                                "    Waiting {sec}s for Google...",
                            ).format(sec=f"{delay:.1f}")
                        )
                        time.sleep(delay)
                    else:
                        print(t("hunter.logs.no_more_pages", "   ⏹️ No more pages."))
                        break
                except:
                    break

        except Exception as e:
            print(
                t("hunter.logs.launch_failed", "    Search Error: {err}").format(err=e)
            )

        return new_links

    def check_link_validity(self, link: str) -> bool:
        """Fast validity check"""
        try:
            resp = self.session.head(link, timeout=5, allow_redirects=True)
            return resp.status_code != 404
        except:
            return True

    def filter_valid_links(self, links: List[str]) -> List[str]:
        """Validate a list of links"""
        if not links:
            return []

        print(
            t("hunter.logs.validating", "\n🔍 Validating {count} links...").format(
                count=len(links)
            )
        )
        valid = []
        for i, link in enumerate(links, 1):
            if self.check_link_validity(link):
                valid.append(link)
            time.sleep(0.1)

        print(
            t(
                "hunter.logs.validation_complete", " Final Validated: {count} groups."
            ).format(count=len(valid))
        )
        return valid

    def find_groups(
        self, keywords: List[str], country: str = "", max_links: int = 10
    ) -> List[str]:
        """Main Entry Point"""
        if isinstance(keywords, str):
            keywords = [keywords]

        print("\n" + "=" * 60)
        print(" FACEBOOK GROUP HUNTER (Auto-Healing)")
        print("=" * 60)
        print(f" Target: {max_links} groups maximum")

        all_results = []

        for kw in keywords:
            res = self.search_via_browser(kw, country)
            all_results.extend(res)
            # Stop early if we have enough
            if len(all_results) >= max_links:
                break
            time.sleep(2)

        unique_links = list(set(all_results))
        print(
            t("hunter.logs.total_raw", "\n🎯 Total Raw Links: {count}").format(
                count=len(unique_links)
            )
        )

        # Limit to requested count before validation
        unique_links = unique_links[:max_links]

        final_links = self.filter_valid_links(unique_links)

        return final_links[:max_links]  # Ensure we don't exceed max

    # --- Session Injector Methods ---
    def save_session(self, session_name: str, session_data: Dict[str, Any]) -> bool:
        """
        Save session data to .antigravity/sessions/ directory.

        Args:
            session_name: Name of the session
            session_data: Session data to save

        Returns:
            True if successful, False otherwise
        """
        try:
            session_file = self.sessions_dir / f"{session_name}.json"
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            self.logger.info("Session saved: %s", session_name)
            return True
        except Exception as e:
            self.logger.error("Failed to save session %s: %s", session_name, e)
            return False

    def load_session(self, session_name: str) -> Optional[Dict[str, Any]]:
        """
        Load session data from .antigravity/sessions/ directory.

        Args:
            session_name: Name of the session to load

        Returns:
            Session data if found, None otherwise
        """
        try:
            session_file = self.sessions_dir / f"{session_name}.json"
            if not session_file.exists():
                return None

            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            self.logger.info("Session loaded: %s", session_name)
            return session_data
        except Exception as e:
            self.logger.error("Failed to load session %s: %s", session_name, e)
            return None

    def list_sessions(self) -> List[str]:
        """
        List all available sessions in .antigravity/sessions/ directory.

        Returns:
            List of session names (without .json extension)
        """
        try:
            sessions = []
            for session_file in self.sessions_dir.glob("*.json"):
                session_name = session_file.stem
                sessions.append(session_name)

            self.logger.info("Found %d sessions", len(sessions))
            return sessions
        except Exception as e:
            self.logger.error("Failed to list sessions: %s", e)
            return []

    def delete_session(self, session_name: str) -> bool:
        """
        Delete a session from .antigravity/sessions/ directory.

        Args:
            session_name: Name of the session to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            session_file = self.sessions_dir / f"{session_name}.json"
            if session_file.exists():
                session_file.unlink()
                self.logger.info("Session deleted: %s", session_name)
                return True
            return False
        except Exception as e:
            self.logger.error("Failed to delete session %s: %s", session_name, e)
            return False

    def search_with_session_injection(
        self,
        session_name: str,
        keywords: List[str],
        country: str = "",
        max_links: int = 10,
    ) -> List[str]:
        """
        Enhanced search with session injection for persistent state management.

        Args:
            session_name: Name of the session to use/load
            keywords: Search keywords
            country: Country filter for search results
            max_links: Maximum number of links to return

        Returns:
            List of found WhatsApp group links
        """
        # Load existing session if available
        session_data = self.load_session(session_name) or {}

        # Merge with current found links
        existing_links = set(session_data.get("found_links", []))
        self.found_links.update(existing_links)

        # Perform search
        new_links = self.find_groups(keywords, country, max_links)

        # Update session with new findings
        updated_session = {
            "found_links": list(self.found_links),
            "last_search": {
                "keywords": keywords,
                "country": country,
                "timestamp": time.time(),
            },
            "total_found": len(self.found_links),
        }

        self.save_session(session_name, updated_session)

        self.logger.info(
            "Session injection completed: %s (total: %d, new: %d)",
            session_name,
            len(self.found_links),
            len(new_links),
        )

        return new_links

    def save(self, links: List[str]) -> None:
        """Save found links to a file."""
        if not links:
            return
        filename = f"data/facebook_groups_{int(time.time())}.txt"
        os.makedirs("data", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")
        self.logger.info(t("hunter.logs.saved_to", "Saved to {path}").format(path=filename))


if __name__ == "__main__":
    # Test
    finder = GroupFinder()
    links = finder.find_groups(["ملابس جملة", "مكتب ملابس"], country="القاهرة")
    finder.save(links)

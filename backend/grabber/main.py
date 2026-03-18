"""
Data Grabber Main - G777 Adaptive Hybrid Engine
Combines Selenium's live window access with Scrapling's adaptive parsing.
Mandate: Zero Hardcoding. All selectors must come from config.yaml.
"""

import time
import logging
import yaml
from typing import List, Dict, Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..core.i18n import t
from ..scrapling_engine import ScraplingEngine

from .base import GrabberBase
from .persistence import GrabberPersistence
from .scraper import GrabberScraper
from .utils import GrabberUtils


class DataGrabber(GrabberBase, GrabberScraper, GrabberUtils):
    """
    CNS-Enhanced Data Grabber.
    Uses ScraplingEngine for adaptive element tracking and Selenium for live interaction.
    """

    def __init__(
        self,
        headless: bool = False,
        engine: str = "scrapling",
        config_path: str = "config.yaml",
    ):
        """
        Initialize DataGrabber with ScraplingEngine as ONLY active engine.
        Zero Hardcoding Compliance - All selectors from config.yaml
        """
        super().__init__(headless=headless)
        self.persistence = GrabberPersistence(self.project_root)
        self.engine_type = engine
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.scraper_config = self.config.get('scraper_settings', {})
        self.selectors = self.scraper_config.get('selectors', {}).get('whatsapp', {})
        self.js_templates = self.scraper_config.get('js_templates', {})

        # Initialize Parent Scraper (which loads ScraplingEngine)
        GrabberScraper.__init__(self, config_path=config_path, driver=None)

        self.logger.info(
            "DataGrabber initialized: engine=%s, headless=%s (Zero Hardcoding Mode)",
            self.engine_type,
            headless,
        )

    def scrape_interactive_mode(self) -> Tuple[Optional[str], str]:
        """
        Primary entry point for user-driven extraction.
        Uses ScraplingEngine exclusively.
        """
        if not self.driver:
            self.initialize_driver()
            if not self.load_whatsapp():
                return None, t(
                    "system.errors.whatsapp_load_failed", "WhatsApp load failed"
                )

        try:
            group_name = self._get_group_name()
            if not self._wait_for_dialog():
                return None, t(
                    "grabber.logs.dialog_not_found",
                    "Dialog not found! Open 'Group Info' -> 'View all' first.",
                )

            # ScraplingEngine extraction only
            return self._scrapling_extraction_strategy(group_name)

        except Exception as e:
            self.logger.error("Scrape failed: %s", e)
            return None, str(e)

    def _scrapling_extraction_strategy(
        self, group_name: str
    ) -> Tuple[Optional[str], str]:
        """
        ScraplingEngine Extraction Strategy - Config-Driven.
        Zero hardcoded selectors or JavaScript.
        """
        collected: Dict[str, dict] = {}

        try:
            self.logger.info(
                "⚡ Executing Scrapling Adaptive Strategy for: %s", group_name
            )

            # Set driver reference for scraper methods
            self.driver = self.driver

            for i in range(150):
                # Extract using config-driven adaptive logic from Scraper class
                batch = self.extract_members_adaptive(
                    self.driver.page_source, self.driver.current_url
                )

                new_found = 0
                for m in batch:
                    if m["phone"] not in collected:
                        m["index"] = len(collected)
                        collected[m["phone"]] = m
                        new_found += 1

                # Dynamic termination logic
                if new_found == 0 and i > 5:
                    break

                # Config-driven smart scroll
                if not self._smart_scroll(self.driver):
                    break

                time.sleep(0.4)

            if not collected:
                return None, t("grabber.logs.no_members", "No members found")

            self.logger.info(
                "✅ Extracted %d members using Scrapling Adaptive Engine",
                len(collected),
            )
            return self._save_members(collected, "scrapling_adaptive", group_name)

        except Exception as e:
            self.logger.error("Adaptive strategy failed: %s", e)
            return None, f"ScraplingEngine error: {str(e)}"

    def _wait_for_dialog(self) -> bool:
        """Wait for the WhatsApp member list dialog to appear - Config-Driven."""
        try:
            dialog_selector = self.selectors.get('dialog_selector')
            if not dialog_selector:
                raise ValueError("dialog_selector not found in config.yaml")
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, dialog_selector))
            )
            return True
        except Exception:
            return False

    # --- Legacy Compatibility Layer (Bridges to current engine) ---
    def _get_group_name(self) -> str:
        # Set driver reference for scraper methods
        self.driver = self.driver
        return self._get_group_name_internal(self.driver)

    def _run_enhanced_strategy(self, group_name: str) -> Tuple[Optional[str], str]:
        """Legacy method bridge."""
        return self._scrapling_extraction_strategy(group_name)

    def _enhanced_extraction_strategy(
        self, group_name: str
    ) -> Tuple[Optional[str], str]:
        """Legacy method bridge."""
        return self._scrapling_extraction_strategy(group_name)

    def _save_members(
        self, members: Dict[str, dict], method: str, group_name: str = "Unknown"
    ) -> Tuple[str, str]:
        """Encapsulated member saving logic."""
        return self.persistence.save_members(members, method, group_name)

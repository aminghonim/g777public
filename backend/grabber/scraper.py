"""
Grabber Scraper - Adaptive Extraction Strategy for G777
Using ScraplingEngine for config-driven, zero-hardcoding extraction.
"""

import time
import logging
import re
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from ..core.i18n import t
from ..scrapling_engine import ScraplingEngine

logger = logging.getLogger(__name__)


class GrabberScraper:
    """
    Handles data extraction and scrolling logic using ScraplingEngine.
    """

    def __init__(self, config_path: str = "config.yaml", driver=None):
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self.scrapling_engine = ScraplingEngine(config_path)
        self.target_config = self.scrapling_engine.get_target_config("whatsapp_groups")
        
        # Load config for templates and selectors
        scraper_config = config.get('scraper_settings', {})
        self.selectors = scraper_config.get('selectors', {}).get('whatsapp', {})
        self.js_templates = scraper_config.get('js_templates', {})
        
        # Store driver reference for internal methods
        self.driver = driver

    def extract_members_adaptive(self, page_source: str, current_url: str) -> List[dict]:
        """
        Adaptive member extraction using config.yaml JavaScript templates.
        Zero hardcoded selectors or JavaScript.
        """
        if not hasattr(self, 'driver') or not self.driver:
            return []
            
        # Get member extraction template from config
        extract_template = self.js_templates.get('member_extraction')
        if not extract_template:
            raise ValueError("member_extraction template not found in config.yaml")
        
        # Replace template variables with config values
        dialog_selector = self.selectors.get('dialog_selector')
        member_item = self.selectors.get('member_item')
        
        if not dialog_selector or not member_item:
            raise ValueError("Required selectors not found in config.yaml")
        
        extract_script = (extract_template
            .replace('{{dialog_selector}}', dialog_selector)
            .replace('{{member_item_selector}}', member_item))
        
        try:
            return self.driver.execute_script(extract_script)
        except Exception:
            return []

    def _smart_scroll(self, driver) -> bool:
        """Config-driven smart scroll logic using config.yaml templates."""
        # Get scroll template from config
        scroll_template = self.js_templates.get('smart_scroll')
        if not scroll_template:
            raise ValueError("smart_scroll template not found in config.yaml")
        
        # Replace template variables with config values
        scroll_container = self.selectors.get('scroll_container')
        if not scroll_container:
            raise ValueError("scroll_container not found in config.yaml")
        scroll_script = scroll_template.replace('{{scroll_container}}', scroll_container)
        
        try:
            return bool(driver.execute_script(scroll_script))
        except Exception:
            return False

    def _get_group_name_internal(self, driver) -> str:
        """Returns the current group name using config-driven selectors."""
        try:
            group_name_selector = self.selectors.get('group_name_selector')
            if not group_name_selector:
                raise ValueError("group_name_selector not found in config.yaml")
            selectors = group_name_selector.split(', ')
            
            # Strategy 1: Try sidebar elements first (find_elements)
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        title = element.get_attribute("title") or element.text
                        if title and title.strip():
                            return title.strip()
                except Exception:
                    continue
            
            # Strategy 2: Fallback to single element (header)
            for selector in selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    # Check .text first (for test compatibility), then fallback to title
                    title = element.text or element.get_attribute("title")
                    if title and title.strip():
                        return title.strip()
                except Exception:
                    continue
                    
            return "Unknown_Group"
        except Exception:
            return "Unknown_Group"

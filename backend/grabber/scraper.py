"""
Grabber Scraper - Adaptive Extraction Strategy for G777

Using ScraplingEngine for config-driven, zero-hardcoding extraction.

Extraction pipeline:
    Layer 1 (Fast): Config-driven JS templates via Selenium execute_script.
    Layer 2 (AI Parse): When JS templates fail (selector changes), the
    LLM parses the raw page_source to extract member data without
    relying on hardcoded selectors.

    IMPORTANT: The AI layer does NOT navigate WhatsApp or open new
    sessions. It only receives page_source text and returns structured
    data. The authenticated Selenium session is never shared.
"""

import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

from selenium.webdriver.common.by import By
from ..core.i18n import t
from ..scrapling_engine import ScraplingEngine

logger = logging.getLogger(__name__)

# Guarded import for event_broker telemetry
try:
    from ..core.event_broker import event_broker
except (ImportError, ValueError):
    try:
        from backend.core.event_broker import event_broker
    except ImportError:
        event_broker = None

# Guarded import for LLM-based fallback parsing
try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    _LLM_AVAILABLE = True
except ImportError:
    _LLM_AVAILABLE = False
    logger.warning(
        "langchain-google-genai not installed. "
        "AI member extraction fallback disabled."
    )


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

    def extract_members_adaptive(
        self, page_source: str, current_url: str
    ) -> List[dict]:
        """
        Adaptive member extraction using config.yaml JavaScript templates.

        Falls back to AI-based DOM parsing when JS templates fail.
        Zero hardcoded selectors or JavaScript.

        Args:
            page_source: Raw HTML page source from the live Selenium session.
            current_url: Current WhatsApp Web URL (for context).

        Returns:
            List of member dicts with 'phone' and optionally 'name' keys.
        """
        if not hasattr(self, 'driver') or not self.driver:
            return []

        # Layer 1: Config-driven JS template extraction
        members = self._extract_via_js_templates()
        if members:
            return members

        # Layer 2: AI fallback — parse page_source with LLM
        logger.warning(
            "JS template extraction returned empty. "
            "Attempting AI fallback parsing."
        )
        return self._ai_extract_members_sync(page_source)

    def _extract_via_js_templates(self) -> List[dict]:
        """
        Execute config-driven JavaScript templates for member extraction.

        Returns:
            List of member dicts, or empty list on failure.
        """
        extract_template = self.js_templates.get('member_extraction')
        if not extract_template:
            logger.error(
                "member_extraction template not found in config.yaml"
            )
            return []

        dialog_selector = self.selectors.get('dialog_selector')
        member_item = self.selectors.get('member_item')

        if not dialog_selector or not member_item:
            logger.error("Required selectors not found in config.yaml")
            return []

        extract_script = (
            extract_template
            .replace('{{dialog_selector}}', dialog_selector)
            .replace('{{member_item_selector}}', member_item)
        )

        try:
            return self.driver.execute_script(extract_script) or []
        except Exception as js_err:
            logger.warning(
                "JS template execution failed: %s", js_err
            )
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
                logger.error(
                    "group_name_selector not found in config.yaml"
                )
                return "Unknown_Group"
            selectors = group_name_selector.split(', ')

            # Strategy 1: Try sidebar elements first (find_elements)
            for selector in selectors:
                try:
                    elements = driver.find_elements(
                        By.CSS_SELECTOR, selector
                    )
                    for element in elements:
                        title = (
                            element.get_attribute("title") or element.text
                        )
                        if title and title.strip():
                            return title.strip()
                except Exception:
                    continue

            # Strategy 2: Fallback to single element (header)
            for selector in selectors:
                try:
                    element = driver.find_element(
                        By.CSS_SELECTOR, selector
                    )
                    title = (
                        element.text
                        or element.get_attribute("title")
                    )
                    if title and title.strip():
                        return title.strip()
                except Exception:
                    continue

            return "Unknown_Group"
        except Exception:
            return "Unknown_Group"

    # ------------------------------------------------------------------ #
    #  AI Fallback: LLM-based DOM Parsing
    # ------------------------------------------------------------------ #

    def _ai_extract_members_sync(self, page_source: str) -> List[dict]:
        """
        Synchronous wrapper for AI member extraction.

        Handles the async/sync boundary safely for callers that
        are not in an async context (e.g. DataGrabber's extraction loop).

        Args:
            page_source: Raw HTML from the live WhatsApp session.

        Returns:
            List of member dicts.
        """
        if not _LLM_AVAILABLE:
            logger.warning(
                "LLM not available for AI fallback parsing."
            )
            return []

        import asyncio

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(
                    asyncio.run,
                    self._ai_extract_members(page_source),
                ).result()
        else:
            return asyncio.run(
                self._ai_extract_members(page_source)
            )

    async def _ai_extract_members(self, page_source: str) -> List[dict]:
        """
        AI-driven member extraction from raw HTML page source.

        The LLM receives a truncated version of the page source and
        extracts phone numbers and names without needing CSS selectors.

        SECURITY: The page_source is passed as READ-ONLY text to the
        LLM. No browser session, cookies, or navigation occurs.

        Args:
            page_source: Raw HTML from the live WhatsApp Web session.

        Returns:
            List of dicts with 'phone' and 'name' keys.
        """
        if event_broker:
            await event_broker.publish_agent_step(
                step_type="healing",
                reasoning="CSS selectors failed. Using AI to parse "
                          "WhatsApp member list from raw HTML.",
                action="_ai_extract_members",
            )

        from backend.ai_client import UnifiedAIClient

        model_name = UnifiedAIClient.TASK_MODEL_MAP.get(
            "WEB_OPERATION",
            os.getenv("BROWSER_USE_MODEL", "gemini-2.0-flash"),
        )
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            logger.error(
                "GEMINI_API_KEY not set. AI fallback aborted."
            )
            return []

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
        )

        # Truncate page_source to avoid token limits
        # WhatsApp member list is typically in the first 15k chars
        truncated_source = page_source[:15000]

        prompt = (
            "You are a data extraction specialist. The following is "
            "raw HTML from a WhatsApp Web group member list dialog.\n"
            "Extract ALL phone numbers and member names you can find.\n"
            "Return the results as a JSON array of objects with "
            "'phone' and 'name' keys.\n"
            "If a name is not available, use an empty string.\n"
            "Only return the JSON array, no other text.\n\n"
            f"HTML:\n{truncated_source}"
        )

        try:
            response = await llm.ainvoke(prompt)
            content = response.content.strip()

            # Clean markdown fences if present
            if content.startswith("```"):
                content = re.sub(
                    r"^```(?:json)?\n?", "", content
                )
                content = re.sub(r"\n?```$", "", content)

            import json
            members = json.loads(content)

            if not isinstance(members, list):
                logger.warning(
                    "AI returned non-list type: %s",
                    type(members).__name__,
                )
                return []

            # Validate structure
            validated: List[dict] = []
            for member in members:
                if isinstance(member, dict) and "phone" in member:
                    validated.append({
                        "phone": str(member["phone"]).strip(),
                        "name": str(
                            member.get("name", "")
                        ).strip(),
                    })

            if event_broker:
                await event_broker.publish_agent_step(
                    step_type="extracting",
                    reasoning=f"AI extracted {len(validated)} members "
                              f"from raw HTML.",
                    action="ai_extraction_complete",
                )

            logger.info(
                "AI fallback extracted %d members", len(validated)
            )
            return validated

        except Exception as ai_err:
            logger.error(
                "AI member extraction failed: %s", ai_err
            )
            if event_broker:
                await event_broker.publish_agent_step(
                    step_type="healing",
                    reasoning=f"AI extraction error: {ai_err}",
                    action="ai_fallback_failed",
                )
            return []

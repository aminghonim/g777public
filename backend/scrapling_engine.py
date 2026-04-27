"""
Scrapling Engine - Adaptive Web Scraping Adapter Layer for G777

This module wraps the Scrapling library behind a unified interface,
providing config-driven, stealth-capable web scraping with adaptive
element tracking and automatic retry logic.

Architecture:
    ScraplingEngine reads settings from config.yaml (scraper_settings block)
    and exposes fetch/extract/stealth_fetch methods that the grabber,
    group_finder, and maps_extractor modules consume.

    Extended with browser-use AI Self-Healing layer:
    When the Adaptive Parser fails repeatedly (failure_threshold), the
    engine automatically triggers an AI-driven browser agent to
    "see" the page and extract data without hardcoded selectors.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import yaml
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)

# browser-use imports are guarded for graceful degradation.
try:
    from browser_use import Agent, Browser, BrowserProfile

    BROWSER_USE_AVAILABLE = True
except ImportError:
    BROWSER_USE_AVAILABLE = False
    logger.warning(
        "browser-use not installed. AI Self-Healing disabled. "
        "Install with: pip install browser-use"
    )

# Scrapling imports are guarded so the module can be imported
# even when Scrapling is not yet installed (graceful degradation).
try:
    from scrapling.fetchers import (
        Fetcher,
        StealthyFetcher,
        DynamicFetcher,
        AsyncFetcher,
    )

    SCRAPLING_AVAILABLE = True
except ImportError:
    SCRAPLING_AVAILABLE = False
    logger.warning(
        "Scrapling not installed. Falling back to Selenium-based scraping. "
        "Install with: pip install 'scrapling[all]'"
    )


_CONFIG_PATH = "config.yaml"


def _load_scraper_config(config_path: str = _CONFIG_PATH) -> Dict[str, Any]:
    """Load scraper_settings from the project config file."""
    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            full_config = yaml.safe_load(config_file)
        return full_config.get("scraper_settings", {})
    except FileNotFoundError:
        logger.error("Config file not found at %s", config_path)
        return {}
    except yaml.YAMLError as parse_error:
        logger.error("Failed to parse config: %s", parse_error)
        return {}


class ScraplingEngine:
    """
    Adapter layer for Scrapling library.

    Provides a unified interface for fetching and extracting data from
    web pages using either Scrapling (adaptive/stealth) or falling back
    to basic HTTP requests.

    Usage:
        engine = ScraplingEngine()
        page = engine.fetch("https://example.com")
        items = engine.extract(page, ".product-card", adaptive=True)
    """

    def __init__(self, config_path: str = _CONFIG_PATH) -> None:
        self.config: Dict[str, Any] = _load_scraper_config(config_path)
        self.engine_type: str = self.config.get("engine", "scrapling")
        self.headless: bool = self.config.get("headless", True)
        self.stealth: bool = self.config.get("stealth_mode", True)
        self.adaptive: bool = self.config.get("adaptive", True)
        self.timeout: int = self.config.get("timeout", 45)
        self.targets: Dict[str, Any] = self.config.get("targets", {})

        # Production-Ready Layers
        self.telemetry_config = self.config.get("telemetry", {})
        self.session_config = self.config.get("identity", {})
        self.validation_config = self.config.get("validation", {})

        # AI Self-Healing Configuration (browser-use)
        self.browser_use_config: Dict[str, Any] = self.config.get("browser_use", {})
        self.ai_enabled: bool = (
            self.browser_use_config.get("enabled", False) and BROWSER_USE_AVAILABLE
        )
        self.ai_max_steps: int = self.browser_use_config.get("max_steps", 15)
        self._ai_browser: Optional[Any] = None  # Lazy init

        # State Tracking
        self._consecutive_failures: Dict[str, int] = {}

        if not SCRAPLING_AVAILABLE and self.engine_type == "scrapling":
            logger.warning("Scrapling requested but not available.")

        logger.info(
            "ScraplingEngine initialized: engine=%s, stealth=%s, "
            "adaptive=%s, ai_healing=%s",
            self.engine_type,
            self.stealth,
            self.adaptive,
            self.ai_enabled,
        )

    @property
    def is_available(self) -> bool:
        """Check if the Scrapling library is installed and usable."""
        return SCRAPLING_AVAILABLE and self.engine_type == "scrapling"

    def _track_telemetry(self, selector: str, success: bool):
        """Monitor Adaptive Parser performance and alert on repeated failures."""
        if not self.telemetry_config.get("enabled", True):
            return

        if success:
            self._consecutive_failures[selector] = 0
        else:
            self._consecutive_failures[selector] = (
                self._consecutive_failures.get(selector, 0) + 1
            )
            threshold = self.telemetry_config.get("failure_threshold", 3)

            if self._consecutive_failures[selector] >= threshold:
                logger.critical(
                    "ALERT: Adaptive Parser failed %d times for selector '%s'. Structure change detected!",
                    self._consecutive_failures[selector],
                    selector,
                )

    def _inject_session(self, session_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Load session configuration for fetchers.
        If session_name is provided, it returns the user_data_dir for Playwright.
        """
        if not self.session_config.get("auto_inject", True):
            return {}

        session_path = self.session_config.get("session_path", ".antigravity/sessions/")

        # Absolute path for reliability
        import os
        from pathlib import Path

        abs_session_path = Path(session_path).absolute()
        abs_session_path.mkdir(parents=True, exist_ok=True)

        kwargs = {}
        if session_name:
            # For Stealthy/Dynamic fetchers (Playwright based)
            # user_data_dir is the way Playwright maintains sessions
            specific_path = abs_session_path / session_name
            specific_path.mkdir(parents=True, exist_ok=True)
            kwargs["user_data_dir"] = str(specific_path)
            logger.debug("Injecting session path: %s", specific_path)

        return kwargs

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def fetch(self, url: str, **kwargs: Any) -> Any:
        """
        Fetch a page using the configured engine.

        Args:
            url: Target URL to fetch
            **kwargs: Additional parameters passed to the fetcher

        Returns:
            Scrapling Response object or None on failure

        Raises:
            ConnectionError: If network is unreachable after retries
            RuntimeError: If Scrapling is not available and no fallback
        """
        if not self.is_available:
            raise RuntimeError(
                "Scrapling engine is not available. "
                "Install with: pip install 'scrapling[all]'"
            )

        logger.info("Fetching URL: %s", url)
        fetcher = Fetcher()
        response = fetcher.get(url, timeout=self.timeout, **kwargs)
        logger.info("Fetch complete: status=%s", getattr(response, "status", "N/A"))
        return response

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def stealth_fetch(self, url: str, **kwargs: Any) -> Any:
        """
        Fetch a page using the stealth fetcher (anti-bot bypass).

        Uses Playwright under the hood with fingerprint spoofing
        to bypass Cloudflare Turnstile, Akamai, and similar protections.

        Args:
            url: Target URL to fetch
            **kwargs: Additional parameters (headless, network_idle, etc.)

        Returns:
            Scrapling Response/Page object
        """
        if not self.is_available:
            raise RuntimeError(
                "Scrapling StealthyFetcher is not available. "
                "Install with: pip install 'scrapling[all]' && scrapling install"
            )

        headless = kwargs.pop("headless", self.headless)
        network_idle = kwargs.pop("network_idle", True)

        session_name = kwargs.pop("session_name", None)
        session_kwargs = self._inject_session(session_name)
        # Merge session_kwargs into kwargs (session_kwargs takes precedence for user_data_dir)
        kwargs.update(session_kwargs)

        logger.info("Stealth fetching URL: %s (headless=%s)", url, headless)
        page = StealthyFetcher.fetch(
            url,
            headless=headless,
            network_idle=network_idle,
            **kwargs,
        )
        logger.info("Stealth fetch complete for: %s", url)
        return page

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def dynamic_fetch(self, url: str, **kwargs: Any) -> Any:
        """
        Fetch a page using the dynamic fetcher (full browser automation).

        Uses Playwright for pages that require JavaScript rendering
        but don't need full stealth capabilities.

        Args:
            url: Target URL to fetch
            **kwargs: Additional parameters

        Returns:
            Scrapling Response/Page object
        """
        if not self.is_available:
            raise RuntimeError(
                "Scrapling DynamicFetcher is not available. "
                "Install with: pip install 'scrapling[all]' && scrapling install"
            )

        headless = kwargs.pop("headless", self.headless)

        session_name = kwargs.pop("session_name", None)
        session_kwargs = self._inject_session(session_name)
        kwargs.update(session_kwargs)

        logger.info("Dynamic fetching URL: %s", url)
        page = DynamicFetcher.fetch(url, headless=headless, **kwargs)
        logger.info("Dynamic fetch complete for: %s", url)
        return page

    def extract(
        self,
        page: Any,
        selector: str,
        adaptive: Optional[bool] = None,
        auto_save: bool = True,
    ) -> List[Any]:
        """
        Extract elements from a fetched page using CSS selectors.

        Args:
            page: Scrapling page/response object from fetch()
            selector: CSS selector string
            adaptive: Use adaptive element tracking (default from config)
            auto_save: Save element fingerprint for future adaptive matching

        Returns:
            List of matched elements
        """
        use_adaptive = adaptive if adaptive is not None else self.adaptive

        try:
            if use_adaptive:
                results = page.css(selector, auto_save=auto_save, adaptive=True)
            else:
                results = page.css(selector)

            logger.info(
                "Extracted %d elements with selector '%s' (adaptive=%s)",
                len(results) if results else 0,
                selector,
                use_adaptive,
            )
            return results if results else []
        except Exception as extraction_error:
            logger.error(
                "Extraction failed for selector '%s': %s",
                selector,
                extraction_error,
            )
            return []

    def extract_text(self, page: Any, selector: str) -> List[str]:
        """
        Extract text content from matched elements.

        Args:
            page: Scrapling page/response object
            selector: CSS selector string

        Returns:
            List of text strings from matched elements
        """
        elements = self.extract(page, selector)
        texts = []
        for element in elements:
            try:
                text = element.text or element.get_text(strip=True)
                if text:
                    texts.append(text.strip())
            except (AttributeError, TypeError):
                continue
        return texts

    def get_target_config(self, target_name: str) -> Dict[str, Any]:
        """
        Get configuration for a named scraping target.

        Args:
            target_name: Key from config.yaml targets
                         (e.g., 'whatsapp_groups', 'google_maps')

        Returns:
            Dict with target URL and selectors, or empty dict
        """
        target = self.targets.get(target_name, {})
        if not target:
            logger.warning("No target config found for: %s", target_name)
        return target

    def health_check(self) -> Dict[str, Any]:
        """
        Run a diagnostic health check on the scraping engine.

        Returns:
            Dict with engine status, availability, and config summary
        """
        return {
            "engine": self.engine_type,
            "scrapling_available": SCRAPLING_AVAILABLE,
            "browser_use_available": BROWSER_USE_AVAILABLE,
            "ai_enabled": self.ai_enabled,
            "is_active": self.is_available,
            "headless": self.headless,
            "stealth": self.stealth,
            "adaptive": self.adaptive,
            "timeout": self.timeout,
            "configured_targets": list(self.targets.keys()),
        }

    # ------------------------------------------------------------------ #
    #  AI Self-Healing Layer (browser-use integration)
    # ------------------------------------------------------------------ #

    def _get_llm(self) -> Any:
        """
        Resolve the LLM instance for browser-use from TASK_MODEL_MAP.

        The model name is NEVER hardcoded; it is read from the
        UnifiedAIClient.TASK_MODEL_MAP['WEB_OPERATION'] which itself
        reads from the BROWSER_USE_MODEL env var.
        """
        from langchain_google_genai import ChatGoogleGenerativeAI
        from backend.ai_client import UnifiedAIClient

        model_name = UnifiedAIClient.TASK_MODEL_MAP.get(
            "WEB_OPERATION",
            os.getenv("BROWSER_USE_MODEL", "gemini-2.0-flash"),
        )
        api_key = os.getenv("GEMINI_API_KEY")
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
        )

    def _should_trigger_ai(self, selector: Optional[str]) -> bool:
        """
        Determine whether the AI Self-Healing layer should activate.

        Conditions:
            1. ai_enabled is True (config + library present)
            2. selector has failed >= failure_threshold consecutive times
        """
        if not self.ai_enabled:
            return False
        if selector is None:
            return True  # No selector means we need AI from the start
        failures = self._consecutive_failures.get(selector, 0)
        threshold = self.telemetry_config.get("failure_threshold", 3)
        return failures >= threshold

    async def ai_fetch(self, url: str, task: str, **kwargs: Any) -> Any:
        """
        AI-driven fetch using browser-use Agent.

        Falls back to stealth_fetch if browser-use is unavailable.

        Args:
            url: Target URL to navigate to.
            task: Natural language description of what to do.
            **kwargs: Additional parameters.

        Returns:
            AgentHistoryList with results from the AI agent.
        """
        if not self.ai_enabled:
            logger.warning(
                "AI Self-Healing not available, falling back to stealth_fetch"
            )
            return self.stealth_fetch(url, **kwargs)

        from backend.core.event_broker import event_broker

        await event_broker.publish_agent_step(
            step_type="healing",
            reasoning=f"Selector-based extraction failed. "
            f"Switching to AI agent for: {url}",
            action=f"ai_fetch: {task[:80]}",
        )

        llm = self._get_llm()

        # Reuse session path for Playwright profile
        session_kwargs = self._inject_session("browser_use")

        browser_config = BrowserProfile(
            headless=self.browser_use_config.get("headless", True),
        )
        browser = Browser(config=browser_config)

        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            max_steps=self.ai_max_steps,
        )

        try:
            result = await agent.run()
            await event_broker.publish_agent_step(
                step_type="extracting",
                reasoning="AI agent completed task successfully.",
                action=f"ai_fetch complete for: {url}",
            )
            return result
        except Exception as agent_error:
            logger.error("AI agent failed for %s: %s", url, agent_error)
            await event_broker.publish_agent_step(
                step_type="healing",
                reasoning=f"AI agent error: {agent_error}",
                action="Falling back to stealth_fetch",
            )
            import asyncio

            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                None, lambda: self.stealth_fetch(url, **kwargs)
            )
        finally:
            await browser.close()

    async def execute_smart_action(
        self,
        url: str,
        action: str,
        selector: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Self-Healing Hybrid: Try Scrapling first, AI fallback on failure.

        This is the primary interface for implementation files.
        It maintains the same return signature regardless of which
        engine handles the request.

        Args:
            url: Target URL.
            action: Natural language description (used by AI fallback).
            selector: CSS selector to try first with Scrapling.
            **kwargs: Additional fetch parameters.

        Returns:
            List of extracted elements or AI agent results.
        """
        from backend.core.event_broker import event_broker

        # Layer 1: Fast/Free path via Scrapling adaptive parser
        if selector and self.is_available:
            try:
                import asyncio

                loop = asyncio.get_running_loop()
                # Run sync Playwright calls in a thread to avoid
                # "Sync API inside asyncio loop" errors
                page = await loop.run_in_executor(
                    None, lambda: self.stealth_fetch(url, **kwargs)
                )
                results = await loop.run_in_executor(
                    None, lambda: self.extract(page, selector, adaptive=True)
                )
                if results:
                    self._track_telemetry(selector, success=True)
                    return results
                # Empty results count as failure
                self._track_telemetry(selector, success=False)
            except Exception as scrapling_error:
                logger.warning(
                    "Scrapling failed for selector '%s': %s",
                    selector,
                    scrapling_error,
                )
                self._track_telemetry(selector, success=False)

        # Layer 2: AI Self-Healing via browser-use
        if self._should_trigger_ai(selector):
            await event_broker.publish_log(
                f"Selector '{selector}' failed. " f"Triggering AI Self-Healing...",
                level="WARNING",
            )
            return await self.ai_fetch(url, action, **kwargs)

        return []

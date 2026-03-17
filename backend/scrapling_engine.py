"""
Scrapling Engine - Adaptive Web Scraping Adapter Layer for G777

This module wraps the Scrapling library behind a unified interface,
providing config-driven, stealth-capable web scraping with adaptive
element tracking and automatic retry logic.

Architecture:
    ScraplingEngine reads settings from config.yaml (scraper_settings block)
    and exposes fetch/extract/stealth_fetch methods that the grabber and
    group_finder modules consume.
"""

import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import yaml
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)

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


class ProxyManager:
    """
    Manages proxy rotation with health tracking and automatic failover.
    
    Supports HTTP and SOCKS5 proxies with round-robin, random, and health-based
    rotation strategies. Implements proxy blacklisting for failed proxies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ProxyManager with configuration.
        
        Args:
            config: Proxy configuration from config.yaml
        """
        self.config = config
        self.enabled = config.get("enabled", False)
        self.proxies = config.get("proxies", [])
        self.strategy = config.get("rotation_strategy", "round_robin")
        self.blacklist_duration = config.get("blacklist_duration", 900)  # 15 minutes
        
        # State tracking
        self._current_index = 0
        self._proxy_health: Dict[str, Dict[str, Any]] = {}
        self._blacklist: Dict[str, float] = {}
        
        # Initialize proxy health tracking
        for proxy in self.proxies:
            proxy_id = self._get_proxy_id(proxy)
            self._proxy_health[proxy_id] = {
                "success_count": 0,
                "failure_count": 0,
                "last_used": 0,
                "last_success": 0,
                "last_failure": 0
            }
        
        logger.info(
            "ProxyManager initialized: enabled=%s, strategy=%s, proxies=%d",
            self.enabled,
            self.strategy,
            len(self.proxies)
        )
    
    def _get_proxy_id(self, proxy: Dict[str, Any]) -> str:
        """Generate unique identifier for proxy."""
        return f"{proxy.get('type', 'http')}://{proxy.get('host', '')}:{proxy.get('port', 0)}"
    
    def _is_proxy_blacklisted(self, proxy: Dict[str, Any]) -> bool:
        """Check if proxy is currently blacklisted."""
        if not self.enabled:
            return False
        
        proxy_id = self._get_proxy_id(proxy)
        if proxy_id in self._blacklist:
            # Check if blacklist duration has expired
            if time.time() - self._blacklist[proxy_id] > self.blacklist_duration:
                del self._blacklist[proxy_id]
                logger.info("Proxy %s removed from blacklist", proxy_id)
                return False
            return True
        return False
    
    def _select_proxy_round_robin(self) -> Optional[Dict[str, Any]]:
        """Select next proxy in round-robin order."""
        available_proxies = [p for p in self.proxies if not self._is_proxy_blacklisted(p)]
        
        if not available_proxies:
            logger.warning("No available proxies (all blacklisted)")
            return None
        
        proxy = available_proxies[self._current_index % len(available_proxies)]
        self._current_index += 1
        return proxy
    
    def _select_proxy_random(self) -> Optional[Dict[str, Any]]:
        """Select random proxy from available pool."""
        import random
        available_proxies = [p for p in self.proxies if not self._is_proxy_blacklisted(p)]
        
        if not available_proxies:
            logger.warning("No available proxies (all blacklisted)")
            return None
        
        return random.choice(available_proxies)
    
    def _select_proxy_health_based(self) -> Optional[Dict[str, Any]]:
        """Select proxy based on health metrics (success rate)."""
        available_proxies = [p for p in self.proxies if not self._is_proxy_blacklisted(p)]
        
        if not available_proxies:
            logger.warning("No available proxies (all blacklisted)")
            return None
        
        # Calculate success rate for each proxy
        best_proxy = None
        best_score = -1
        
        for proxy in available_proxies:
            proxy_id = self._get_proxy_id(proxy)
            health = self._proxy_health.get(proxy_id, {})
            
            success_count = health.get("success_count", 0)
            failure_count = health.get("failure_count", 0)
            total_attempts = success_count + failure_count
            
            if total_attempts == 0:
                score = 0.5  # Neutral score for unused proxies
            else:
                score = success_count / total_attempts
            
            # Prefer recently successful proxies
            if health.get("last_success", 0) > time.time() - 300:  # Within 5 minutes
                score += 0.1
            
            if score > best_score:
                best_score = score
                best_proxy = proxy
        
        return best_proxy
    
    def get_proxy(self) -> Optional[Dict[str, Any]]:
        """
        Get the next proxy based on rotation strategy.
        
        Returns:
            Proxy configuration dict or None if no proxies available
        """
        if not self.enabled or not self.proxies:
            return None
        
        if self.strategy == "round_robin":
            return self._select_proxy_round_robin()
        elif self.strategy == "random":
            return self._select_proxy_random()
        elif self.strategy == "health_based":
            return self._select_proxy_health_based()
        else:
            logger.warning("Unknown proxy strategy: %s, using round_robin", self.strategy)
            return self._select_proxy_round_robin()
    
    def mark_proxy_success(self, proxy: Dict[str, Any]) -> None:
        """
        Mark proxy as successful for health tracking.
        
        Args:
            proxy: Proxy configuration that was used successfully
        """
        if not self.enabled:
            return
        
        proxy_id = self._get_proxy_id(proxy)
        if proxy_id in self._proxy_health:
            self._proxy_health[proxy_id]["success_count"] += 1
            self._proxy_health[proxy_id]["last_success"] = time.time()
            self._proxy_health[proxy_id]["last_used"] = time.time()
        
        logger.debug("Proxy %s marked as successful", proxy_id)
    
    def mark_proxy_failed(self, proxy: Dict[str, Any], error: str = "Unknown") -> None:
        """
        Mark proxy as failed and potentially blacklist it.
        
        Args:
            proxy: Proxy configuration that failed
            error: Error description for logging
        """
        if not self.enabled:
            return
        
        proxy_id = self._get_proxy_id(proxy)
        if proxy_id in self._proxy_health:
            self._proxy_health[proxy_id]["failure_count"] += 1
            self._proxy_health[proxy_id]["last_failure"] = time.time()
            self._proxy_health[proxy_id]["last_used"] = time.time()
            
            # Blacklist if too many failures
            failure_count = self._proxy_health[proxy_id]["failure_count"]
            if failure_count >= 3:  # Blacklist after 3 failures
                self._blacklist[proxy_id] = time.time()
                logger.warning(
                    "Proxy %s blacklisted after %d failures: %s",
                    proxy_id,
                    failure_count,
                    error
                )
        
        logger.debug("Proxy %s marked as failed: %s", proxy_id, error)
    
    def is_proxy_healthy(self, proxy: Dict[str, Any]) -> bool:
        """
        Check if proxy is considered healthy.
        
        Args:
            proxy: Proxy configuration to check
            
        Returns:
            True if proxy is healthy, False otherwise
        """
        if not self.enabled:
            return True
        
        if self._is_proxy_blacklisted(proxy):
            return False
        
        proxy_id = self._get_proxy_id(proxy)
        if proxy_id not in self._proxy_health:
            return True  # New proxy is considered healthy
        
        health = self._proxy_health[proxy_id]
        success_count = health.get("success_count", 0)
        failure_count = health.get("failure_count", 0)
        
        if failure_count == 0:
            return True
        
        # Consider healthy if success rate > 50%
        total_attempts = success_count + failure_count
        return (success_count / total_attempts) > 0.5
    
    def get_proxy_stats(self) -> Dict[str, Any]:
        """
        Get proxy statistics for monitoring.
        
        Returns:
            Dictionary with proxy health statistics
        """
        if not self.enabled:
            return {"enabled": False}
        
        stats = {
            "enabled": True,
            "total_proxies": len(self.proxies),
            "blacklisted_count": len(self._blacklist),
            "strategy": self.strategy,
            "proxy_health": {}
        }
        
        for proxy in self.proxies:
            proxy_id = self._get_proxy_id(proxy)
            health = self._proxy_health.get(proxy_id, {})
            stats["proxy_health"][proxy_id] = {
                "success_count": health.get("success_count", 0),
                "failure_count": health.get("failure_count", 0),
                "blacklisted": proxy_id in self._blacklist,
                "healthy": self.is_proxy_healthy(proxy)
            }
        
        return stats


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
        self.site_difficulty_config = self.config.get("site_difficulty", {})
        self.proxy_config = self.config.get("proxy_rotation", {})
        
        # Initialize Proxy Manager
        self.proxy_manager = ProxyManager(self.proxy_config)

        # State Tracking
        self._consecutive_failures: Dict[str, int] = {}

        if not SCRAPLING_AVAILABLE and self.engine_type == "scrapling":
            logger.warning("Scrapling requested but not available.")

        logger.info(
            "ScraplingEngine initialized: engine=%s, stealth=%s, adaptive=%s",
            self.engine_type,
            self.stealth,
            self.adaptive,
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

    def _get_site_difficulty(self, url: str) -> str:
        """
        Determine the difficulty level of a target site based on configuration.

        Args:
            url: Target URL to analyze

        Returns:
            Difficulty level: "easy", "medium", or "hard"
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Remove www. prefix if present
            if domain.startswith("www."):
                domain = domain[4:]

            # Get site-specific difficulty mapping
            sites_config = self.site_difficulty_config.get("sites", {})
            default_level = self.site_difficulty_config.get("default", "medium")

            # Check for exact domain match
            if domain in sites_config:
                return sites_config[domain]

            # Check for partial domain match (e.g., "facebook.com" matches "m.facebook.com")
            for site, level in sites_config.items():
                if domain.endswith(site) or site.endswith(domain):
                    return level

            return default_level

        except Exception as e:
            logger.warning("Error determining site difficulty for %s: %s", url, e)
            return self.site_difficulty_config.get("default", "medium")

    def _format_proxy_for_scrapling(self, proxy: Dict[str, Any]) -> str:
        """
        Format proxy configuration for Scrapling fetchers.
        
        Args:
            proxy: Proxy configuration dict
            
        Returns:
            Proxy URL string in format: http://user:pass@host:port or socks5://user:pass@host:port
        """
        proxy_type = proxy.get("type", "http").lower()
        host = proxy.get("host", "")
        port = proxy.get("port", 0)
        username = proxy.get("username", "")
        password = proxy.get("password", "")
        
        if proxy_type not in ["http", "https", "socks5"]:
            logger.warning("Unsupported proxy type: %s", proxy_type)
            proxy_type = "http"
        
        # Build proxy URL
        if username and password:
            proxy_url = f"{proxy_type}://{username}:{password}@{host}:{port}"
        else:
            proxy_url = f"{proxy_type}://{host}:{port}"
        
        logger.debug("Formatted proxy URL: %s", proxy_url.replace(password, "***") if password else proxy_url)
        return proxy_url

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def smart_fetch(self, url: str, **kwargs: Any) -> Any:
        """
        Automatically select and use the appropriate fetcher based on site difficulty.

        This method analyzes the target URL and selects the optimal fetcher:
        - "easy": Regular Fetcher (fast, lightweight HTTP)
        - "medium": Dynamic Fetcher (JavaScript rendering via Playwright)
        - "hard": StealthyFetcher (anti-bot bypass with fingerprint spoofing)

        Args:
            url: Target URL to fetch
            **kwargs: Additional parameters passed to the fetcher
                - force_fetcher: Override auto-selection ("fetcher", "dynamic", "stealthy")
                - session_name: Session persistence name
                - headless: Run browser in headless mode (default from config)
                - proxy: Override proxy selection (dict with proxy config)
                - use_proxy: Enable/disable proxy for this request (default from config)

        Returns:
            Scrapling Response/Page object

        Raises:
            RuntimeError: If Scrapling is not available
            ConnectionError: If network is unreachable after retries

        Example:
            engine = ScraplingEngine()
            page = engine.smart_fetch("https://facebook.com/groups")
            # Automatically uses StealthyFetcher for facebook.com with proxy rotation
        """
        if not self.is_available:
            raise RuntimeError(
                "Scrapling engine is not available. "
                "Install with: pip install 'scrapling[all]'"
            )

        # Check for manual override
        force_fetcher = kwargs.pop("force_fetcher", None)
        
        # Handle proxy selection
        proxy_override = kwargs.pop("proxy", None)
        use_proxy = kwargs.pop("use_proxy", self.proxy_manager.enabled)
        
        current_proxy = None
        if use_proxy:
            if proxy_override:
                current_proxy = proxy_override
            else:
                current_proxy = self.proxy_manager.get_proxy()
            
            if current_proxy:
                proxy_url = self._format_proxy_for_scrapling(current_proxy)
                kwargs["proxy"] = proxy_url
                logger.info("Using proxy: %s", proxy_url.split("@")[-1] if "@" in proxy_url else proxy_url)
            else:
                logger.warning("Proxy requested but none available")

        if force_fetcher:
            difficulty = force_fetcher
        else:
            difficulty = self._get_site_difficulty(url)

        headless = kwargs.pop("headless", self.headless)
        session_name = kwargs.pop("session_name", None)
        session_kwargs = self._inject_session(session_name)
        kwargs.update(session_kwargs)

        logger.info(
            "Smart fetching URL: %s (difficulty=%s, headless=%s)",
            url,
            difficulty,
            headless,
        )

        try:
            if difficulty == "hard":
                # Use StealthyFetcher for anti-bot protected sites
                network_idle = kwargs.pop("network_idle", True)
                page = StealthyFetcher.fetch(
                    url,
                    headless=headless,
                    network_idle=network_idle,
                    **kwargs,
                )
                logger.info("Stealth fetch complete for: %s", url)

            elif difficulty == "medium":
                # Use DynamicFetcher for JS-rendered pages
                page = DynamicFetcher.fetch(url, headless=headless, **kwargs)
                logger.info("Dynamic fetch complete for: %s", url)

            else:  # "easy" or default
                # Use regular Fetcher for simple sites
                fetcher = Fetcher()
                page = fetcher.get(url, timeout=self.timeout, **kwargs)
                logger.info("Regular fetch complete for: %s (status=%s)", url, getattr(page, "status", "N/A"))

            # Mark proxy as successful if used
            if current_proxy:
                self.proxy_manager.mark_proxy_success(current_proxy)

            return page

        except Exception as e:
            # Mark proxy as failed if used
            if current_proxy:
                self.proxy_manager.mark_proxy_failed(current_proxy, str(e))
            
            logger.error("Smart fetch failed for %s: %s", url, e)
            raise

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
            Dict with engine status, availability, proxy stats, and config summary
        """
        return {
            "engine": self.engine_type,
            "scrapling_available": SCRAPLING_AVAILABLE,
            "is_active": self.is_available,
            "headless": self.headless,
            "stealth": self.stealth,
            "adaptive": self.adaptive,
            "timeout": self.timeout,
            "configured_targets": list(self.targets.keys()),
            "proxy_stats": self.proxy_manager.get_proxy_stats(),
        }

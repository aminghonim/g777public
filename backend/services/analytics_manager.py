"""
PostHog Analytics Manager
========================
Handles event tracking and user analytics for G777.
"""

# Standard library
import logging
import os
from typing import Any, Dict, Optional

# Third-party
try:
    import posthog
    HAS_POSTHOG = True
except ImportError:
    HAS_POSTHOG = False
    
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

logger = logging.getLogger(__name__)

class AnalyticsManager:
    _instance: Optional["AnalyticsManager"] = None

    def __new__(cls) -> "AnalyticsManager":
        if cls._instance is None:
            cls._instance = super(AnalyticsManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "initialized", False):
            return
        
        self.api_key = os.getenv("POSTHOG_API_KEY")
        self.host = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com")
        
        if HAS_POSTHOG and self.api_key:
            posthog.project_api_key = self.api_key
            posthog.host = self.host
            logger.info("PostHog initialized on host: %s", self.host)
        elif not HAS_POSTHOG:
            logger.warning("PostHog library not installed. Analytics will be simulated/disabled.")
        else:
            logger.warning("PostHog API Key missing. Analytics will be disabled.")
            
        self.initialized = True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def capture(self, user_id: str, event_name: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Captures an event in PostHog with automatic retries."""
        if not HAS_POSTHOG or not self.api_key:
            return
        
        try:
            posthog.capture(user_id, event_name, properties or {})
        except Exception as e:
            logger.error("PostHog capture failed: %s", e)
            raise  # Re-raise for tenacity to retry

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def identify(self, user_id: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Identifies a user in PostHog with automatic retries."""
        if not HAS_POSTHOG or not self.api_key:
            return
        
        try:
            posthog.identify(user_id, properties or {})
        except Exception as e:
            logger.error("PostHog identify failed: %s", e)
            raise  # Re-raise for tenacity to retry

analytics = AnalyticsManager()

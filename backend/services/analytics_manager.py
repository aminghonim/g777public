"""
PostHog Analytics Manager
========================
Handles event tracking and user analytics for G777.
"""

import os
import posthog
from dotenv import load_dotenv

load_dotenv()

class AnalyticsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnalyticsManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "initialized", False):
            return
        
        self.api_key = os.getenv("POSTHOG_API_KEY")
        self.host = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com")
        
        if self.api_key:
            posthog.project_api_key = self.api_key
            posthog.host = self.host
            print(f"[OK] PostHog initialized on host: {self.host}")
        else:
            print("[WARN] PostHog API Key missing. Analytics will be disabled.")
            
        self.initialized = True

    def capture(self, user_id: str, event_name: str, properties: dict = None):
        """Captures an event in PostHog"""
        if not self.api_key:
            return
        
        try:
            posthog.capture(user_id, event_name, properties or {})
        except Exception as e:
            print(f"[ERROR] PostHog capture failed: {e}")

    def identify(self, user_id: str, properties: dict = None):
        """Identifies a user in PostHog"""
        if not self.api_key:
            return
        
        try:
            posthog.identify(user_id, properties or {})
        except Exception as e:
            print(f"[ERROR] PostHog identify failed: {e}")

analytics = AnalyticsManager()

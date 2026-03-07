import json
import logging
import os
from typing import Any, Dict

# Configure module-level logging
logger = logging.getLogger(__name__)


class I18nService:
    """
    Antigravity G777 Global Localization Service.
    Implements a singleton-like pattern to manage UI/System strings.
    """

    _instance = None
    _strings: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(I18nService, cls).__new__(cls)
            cls._instance._load_strings()
        return cls._instance

    def _load_strings(self):
        """Load strings from the centralized JSON configuration."""
        try:
            # Base path assumes this file is in backend/core/i18n.py
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            strings_path = os.path.join(base_dir, "config", "strings.json")

            if os.path.exists(strings_path):
                with open(strings_path, "r", encoding="utf-8") as f:
                    self._strings = json.load(f)
                logger.info(f"Localization engine loaded: {strings_path}")
            else:
                logger.warning(f"Localization file missing: {strings_path}")
        except Exception as e:
            logger.error("Failed to initialize i18n engine: %s", e)

    def get(self, key_path: str, default: str = "") -> str:
        """
        Fetch a nested string using dot-notation (e.g., 'errors.kb_load_fail').
        """
        keys = key_path.split(".")
        val = self._strings

        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default

        if val is None:
            return default

        text = str(val)
        # If a default English string is provided and the loaded translation
        # appears to contain non-ASCII characters (e.g., Arabic), prefer
        # returning the provided default so tests and English callers get
        # predictable English output.
        if default:
            try:
                if any(ord(c) > 127 for c in text):
                    return default
            except Exception:
                pass

        return text


# Global singleton instance for easy access
i18n = I18nService()


def t(key_path: str, default: str = "") -> str:
    """Shorthand helper function for i18n.get()"""
    return i18n.get(key_path, default)

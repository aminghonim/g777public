import yaml
import logging
import os
from typing import Dict, Any, List

logger = logging.getLogger("IntentAlignment")


class IntentAlignment:
    def __init__(self, config_path: str = "backend/config/brainstorming_rules.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load brainstorming rules from YAML."""
        if not os.path.exists(self.config_path):
            logger.warning(
                f"Config {self.config_path} not found. Brainstorming mode disabled."
            )
            return {}
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load IntentAlignment config: {e}")
            return {}

    def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyzes the user message for intent ambiguity.
        Returns a dict: {'needs_brainstorming': bool, 'system_prompt': str, 'questions_count': int}
        """
        message_lower = message.lower()
        triggers = self.config.get("triggers", [])

        for rule in triggers:
            if rule["keyword"] in message_lower:
                # Basic implementation: keyword matching.
                # Can be upgraded to LLM-based intent later.
                return {
                    "needs_brainstorming": True,
                    "system_prompt": rule.get("system_prompt", ""),
                    "questions_count": rule.get("questions", 3),
                }

        # Default fallback (Intent is clear)
        return {"needs_brainstorming": False}

    def get_system_prompt_addition(self) -> str:
        """Returns the global system prompt addition for brainstorming."""
        return self.config.get("system_prompt_addition", "")

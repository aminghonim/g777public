from google import adk
import yaml
import os
import json
from typing import Dict, Any


class PersonaAgent(adk.Agent):
    """
    ADK-compliant Agent for managing the AI Persona (Yasmine).
    Handles identity, tone, and specific sales rules.
    """

    def __init__(
        self, config_path: str = "config/ai_instructions.yaml", tools: list = None
    ):
        # Load persona config BEFORE super().__init__ to avoid Pydantic field assignment
        loaded_config = PersonaAgent._load_config_static(config_path)
        persona_cfg = loaded_config.get("main_assistant", {})
        instruction = PersonaAgent._build_instructions_static(persona_cfg)

        # ADK requires name to be a valid Python identifier (no spaces/special chars)
        raw_name = persona_cfg.get("role", "Yasmine")
        safe_name = "".join(c if c.isalnum() or c == "_" else "_" for c in raw_name)
        if safe_name and safe_name[0].isdigit():
            safe_name = "_" + safe_name

        super().__init__(
            name=safe_name or "Yasmine",
            instruction=instruction,
            tools=tools or [],
        )

        # Store config reference AFTER Pydantic model is initialized
        object.__setattr__(self, "_persona_config", loaded_config)

    @staticmethod
    def _load_config_static(path: str) -> Dict[str, Any]:
        try:
            full_path = os.path.join(os.getcwd(), path)
            if not os.path.exists(full_path):
                return {}
            with open(full_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Instance alias for backward compatibility."""
        return PersonaAgent._load_config_static(path)

    @staticmethod
    def _build_instructions_static(cfg: Dict[str, Any]) -> str:
        """Construct the core system instructions for the agent."""
        personality = "\n".join([f"- {p}" for p in cfg.get("personality", [])])
        rules = "\n".join([f"- {r}" for r in cfg.get("rules", [])])
        return f"""
ROLE: {cfg.get('role', 'AI Assistant')}
TASK: {cfg.get('task', 'Assist customers')}

PERSONALITY:
{personality}

STRICT RULES:
{rules}

Tone: Speak Egyptian Arabic (Friendly but Professional).
"""

    def _build_instructions(self, cfg: Dict[str, Any]) -> str:
        """Instance alias for backward compatibility."""
        return PersonaAgent._build_instructions_static(cfg)

    def get_persona_context(self, customer_name: str, offerings: str) -> str:
        """Helper to generate session-specific context."""
        return f"""
[[ CURRENT CUSTOMER ]]
Name: {customer_name}

[[ OFFICIAL PRICE LIST ]]
{offerings}
"""

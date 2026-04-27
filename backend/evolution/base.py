"""
Evolution API Base Module.
Handles configuration, environment detection, and authentication headers for Evolution API.
"""

import os
from typing import Dict, Optional


from core.config import settings


class EvolutionBase:
    """
    Base class for Evolution API handlers, providing shared config and auth headers.
    """

    def __init__(self):
        self.provider = "evolution"

        # Priority: Settings -> Env overrides
        evo_conf = settings.evolution_api

        if not evo_conf:
            # If config is totally missing, we fall back to empty strings to avoid crashes,
            # but we log a warning. We do NOT hardcode IP addresses.
            self.evolution_url = os.getenv("EVOLUTION_PUBLIC_URL", "")
            self.api_key = os.getenv("EVOLUTION_API_KEY", "")
            self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "")
        else:
            # According to SOLVED_ISSUES.md: "دائماً استخدم Evolution API على Port 8080... الخدمة على Port 3000 هي مساعدة فقط"
            # Prevent falling back to BAILEYS_API_URL (Port 3000) overriding the real Evolution API URL.

            env_evo_url = os.getenv("EVOLUTION_PUBLIC_URL") or os.getenv(
                "EVOLUTION_API_URL"
            )
            if env_evo_url:
                self.evolution_url = env_evo_url.rstrip("/")
            else:
                self.evolution_url = evo_conf.url.rstrip("/")

            self.api_key = evo_conf.api_key or os.getenv("EVOLUTION_API_KEY", "")
            self.instance_name = evo_conf.instance_name or os.getenv(
                "EVOLUTION_INSTANCE_NAME", ""
            )

        self.url = self.evolution_url
        self.webhook_url = os.getenv("WEBHOOK_URL") or os.getenv("PUBLIC_WEBHOOK_URL")
        self.n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")

    def _get_headers(self) -> Dict[str, str]:
        """Returns standard headers for Evolution API."""
        return {"apikey": self.api_key, "Content-Type": "application/json"}

    def _get_instance(self, override_instance: str = None) -> str:
        """Returns the effective instance name (override or default)."""
        return override_instance or self.instance_name

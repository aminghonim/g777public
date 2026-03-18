"""
WhatsApp Webhook Handler.
Configures and manages event receivers.
"""

from typing import Any, Dict

import requests

from .base import EvolutionBase


class WebhookHandler(EvolutionBase):
    """
    Handles setting and verifying webhooks.
    """

    def set_evolution_webhook(self, webhook_url: str) -> bool:
        """Sets the primary message recipient webhook in Evolution API."""
        try:
            url = f"{self.evolution_url}/webhook/set/{self.instance_name}"
            payload = {
                "webhook": {
                    "enabled": True,
                    "url": webhook_url,
                    "webhookByEvents": False,
                    "events": ["MESSAGES_UPSERT"],
                }
            }
            resp = requests.post(
                url, json=payload, headers=self._get_headers(), timeout=10
            )
            return resp.status_code in [200, 201]
        except requests.RequestException:
            return False

    def get_creation_payload(self, name: str) -> Dict[str, Any]:
        """Generates payload for instance creation with integrated webhook."""
        return {
            "instanceName": name,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",
            "webhook": self.webhook_url,
            "events": ["MESSAGES_UPSERT"],
        }

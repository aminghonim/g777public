"""
WhatsApp Gateway - The bridge between the application layer and Evolution API.
Simplified local-first architecture.
"""

import os
from typing import Dict, Any, List, Optional

import requests

from .evolution import (
    ConnectionHandler,
    MessagingHandler,
    GroupHandler,
    WebhookHandler,
    CampaignHandler,
)
from .core.i18n import t


class WAGateway(CampaignHandler, ConnectionHandler, GroupHandler, WebhookHandler):
    """
    WhatsApp Gateway - Unified entry point for all Evolution API interactions.
    Uses handler mixins via MRO: CampaignHandler (extends MessagingHandler) first.
    All traffic goes to local Evolution API (localhost), not any cloud service.
    """

    def __init__(self):
        super().__init__()
        self.is_connected = False
        self._verify_connection()

    def warmup(self) -> tuple:
        """Wakes up the Evolution API and verifies it is responding."""
        connected = self._verify_connection()
        if connected:
            if self.webhook_url:
                self.set_evolution_webhook(self.webhook_url)
            return True, t("cloud.errors.connected_ready", "Connected & Ready")
        return False, t(
            "cloud.errors.disconnected_startup", "Disconnected or Starting up..."
        )

    def start_campaign_cloud(
        self,
        numbers: List[str],
        message: str,
        campaign_name: str = "",
        instance_name: str = None,
    ) -> Dict[str, Any]:
        """Initiates a bulk send campaign via Evolution API."""
        success_count = 0
        headers = self._get_headers()
        instance = self._get_instance(instance_name)
        for num in numbers:
            ok, resp = self._send_evolution_text(
                self.evolution_url, instance, headers, num, message
            )
            if ok:
                success_count += 1

        return {
            "success": success_count > 0,
            "total": len(numbers),
            "sent": success_count,
        }

    def send_whatsapp_message(
        self,
        phone: str,
        message: str,
        media_path: Optional[str] = None,
        instance_name: str = None,
    ) -> tuple:
        """Sends a text or media message via Evolution API."""
        headers = self._get_headers()
        instance = self._get_instance(instance_name)
        try:
            if media_path and os.path.exists(media_path):
                return self._send_evolution_media(
                    self.evolution_url,
                    instance,
                    headers,
                    phone,
                    message,
                    media_path,
                )
            else:
                return self._send_evolution_text(
                    self.evolution_url, instance, headers, phone, message
                )
        except Exception as e:
            return False, str(e)

    def ask_ai_cloud(self, prompt: str, system_message: str = "") -> str:
        """Fallback AI query. Kept for legacy compatibility with UI controllers."""
        return t(
            "cloud.errors.ai_unavailable",
            "AI service is handled via the intelligence router.",
        )

    def _verify_connection(self) -> bool:
        """Verifies Evolution API connectivity and updates internal state."""
        try:
            state_data = self.get_connection_state()
            state = state_data.get("instance", {}).get("state")
            self.is_connected = state == "open"
            return self.is_connected
        except Exception:
            self.is_connected = False
            return False

    def check_numbers_exist(
        self, numbers: List[str], instance_name: str = None
    ) -> List:
        """Filters numbers by WhatsApp availability via Evolution API."""
        try:
            instance = self._get_instance(instance_name)
            url = f"{self.evolution_url}/chat/whatsappNumbers/{instance}"
            payload = {"numbers": numbers}
            response = requests.post(url, json=payload, headers=self._get_headers())
            return response.json()
        except Exception:
            return []


# Global gateway instance
wa_gateway = WAGateway()

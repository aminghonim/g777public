"""
Baileys Client - Send WhatsApp Messages
========================================
Communicates with Baileys service to send replies.
"""

import os
import httpx
import logging
from typing import Dict
from core.config import settings


logger = logging.getLogger(__name__)


class BaileysClient:
    """Client for sending messages via Baileys or Evolution service"""

    def __init__(self):
        # Load environment configuration
        self.provider = os.getenv("WHATSAPP_PROVIDER", "evolution").lower()

        # API Key is mandatory for all providers (SaaS Rule)
        self.api_key = (
            settings.evolution_api.api_key
            if settings.evolution_api
            else os.getenv("EVOLUTION_API_KEY", "")
        )
        self.headers = {"apikey": self.api_key, "Content-Type": "application/json"}

        # Base Configuration
        if self.provider == "evolution":
            # Use centralized settings with no hardcoded fallbacks
            if settings.evolution_api:
                self.base_url = settings.evolution_api.url.rstrip("/")
                self.instance = settings.evolution_api.instance_name
            else:
                # Fallback only if settings are completely missing (should not happen in prod)
                logger.warning("Evolution API settings missing in config.yaml")
                self.base_url = ""
                self.instance = ""
        else:
            self.base_url = (
                settings.evolution_api.baileys_api_url.rstrip("/")
                if settings.evolution_api and settings.evolution_api.baileys_api_url
                else "http://localhost:3000"
            )

    def _get_headers(self) -> Dict[str, str]:
        return {"apikey": self.api_key, "Content-Type": "application/json"}

    async def send_message(self, phone: str, text: str):
        """
        Send a WhatsApp message via the active provider.
        Supports full JIDs (e.g. @lid or @s.whatsapp.net).
        """
        # Normalize phone/JID
        # If it's already a full JID (contains @), use it as is
        if "@" in phone:
            phone_clean = phone.strip()
        else:
            phone_clean = phone.replace("+", "").strip()
            if self.provider == "evolution":
                phone_clean = f"{phone_clean}@s.whatsapp.net"

        if self.provider == "evolution":
            # Evolution API v2: /message/sendText/{instance}
            url = f"{self.base_url}/message/sendText/{self.instance}"

            payload = {
                "number": phone_clean,
                "text": text,
                "options": {"delay": 1200, "presence": "composing"},
            }
        else:
            # Legacy Baileys structure
            url = f"{self.base_url}/send"
            payload = {"phone": phone_clean, "message": text}

        try:
            logger.info(f"Sending WhatsApp to {phone_clean}")
            logger.debug(f"URL: {url}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url, json=payload, headers=self._get_headers()
                )

                logger.debug(f"Response Status: {response.status_code}")

                if response.status_code in [200, 201]:
                    logger.info(f"Message SENT: {response.json()}")
                    return {"success": True, "data": response.json()}
                else:
                    logger.error(f"SEND FAILED: {response.text}")
                    return {
                        "success": False,
                        "error": f"Status {response.status_code}",
                        "details": response.text,
                    }
        except Exception as e:
            logger.error(f"NETWORK ERROR in BaileysClient: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def get_status(self):
        """Check connection status of the active engine"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if self.provider == "evolution":
                    url = f"{self.base_url}/instance/connectionState/{self.instance}"
                    response = await client.get(url, headers=self._get_headers())
                    if response.status_code == 200:
                        data = response.json()
                        state = data.get("instance", {}).get("state")
                        return {"connected": state == "open", "state": state}
                else:
                    # For local Baileys service on port 3000
                    response = await client.get(
                        f"{self.base_url}/status", headers=self.headers
                    )
                    if response.status_code == 200:
                        data = response.json()
                        # If the service is up but WhatsApp not paired, return connected: false
                        return {
                            "connected": data.get("connected", False),
                            "state": data.get("status", "disconnected"),
                            "user": data.get("user"),
                        }

                return {
                    "connected": False,
                    "state": "offline",
                    "error": "Service unreachable",
                }
        except Exception as e:
            return {"connected": False, "error": str(e)}


# Singleton instance
baileys_client = BaileysClient()

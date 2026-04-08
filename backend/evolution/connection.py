"""
WhatsApp Connection Handler.
Manages QR codes, pairing codes, and session logout.
"""

import time
from typing import Any, Dict

import requests

from ..core.i18n import t
from .base import EvolutionBase


class ConnectionHandler(EvolutionBase):
    """
    Handles QR codes, Pairing codes, Logout, and Connection State.
    """

    def get_connection_state(self, instance_name: str = None) -> Dict[str, Any]:
        """Fetch connection state. Supports SaaS instance override."""
        try:
            instance = self._get_instance(instance_name)
            if instance_name:  # SaaS Mode (Standard Evolution API)
                url = f"{self.evolution_url}/instance/connectionState/{instance}"
            else:  # Legacy/Local Mode
                url = f"{self.evolution_url}/status"

            resp = requests.get(url, headers=self._get_headers(), timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if instance_name:
                    return {"instance": data.get("instance", {})}

                # Map Legacy Baileys response
                return {
                    "instance": {
                        "state": "open" if data.get("connected") else "close",
                        "status": data.get("status"),
                    }
                }
            return {"instance": {"state": "disconnected"}}
        except Exception:
            return {"instance": {"state": "error"}}

    def get_evolution_qr(self, instance_name: str = None) -> Dict[str, Any]:
        """Fetches QR code. Supports SaaS instance override."""
        try:
            instance = self._get_instance(instance_name)
            if instance_name:
                url = f"{self.evolution_url}/instance/connect/{instance}"  # Evolution uses connect for QR
            else:
                url = f"{self.evolution_url}/qr"

            resp = requests.get(url, headers=self._get_headers(), timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                # Evolution Standard returns base64 or link
                if instance_name:
                    return {
                        "success": True,
                        "data": {"base64": data.get("base64") or data.get("qrcode")},
                    }

                if data.get("success"):
                    return {"success": True, "data": {"base64": data.get("qrImage")}}
            return {"success": False, "error": f"Status {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_pairing_code(self, phone: str, instance_name: str = None) -> Dict[str, Any]:
        """Requests pairing code. Supports SaaS instance override."""
        try:
            instance = self._get_instance(instance_name)
            # Standard Evolution API logic for pairing might differ, checks required
            # For now keeping legacy map if instance is not provided
            if instance_name:
                # Evolution typically uses /instance/connect/{instance}?number=...
                pass  # Placeholder for Evolution v2 pairing logic

            url = f"{self.evolution_url}/pairing-code"
            resp = requests.post(
                url, headers=self._get_headers(), json={"phone": phone}, timeout=15
            )
            return resp.json()
        except Exception as e:
            return {"success": False, "message": str(e)}

    def logout_instance(self, instance_name: str = None) -> bool:
        """Disconnects instance. Supports SaaS instance override."""
        try:
            instance = self._get_instance(instance_name)
            if instance_name:
                url = f"{self.evolution_url}/instance/logout/{instance}"
                resp = requests.delete(url, headers=self._get_headers(), timeout=10)
            else:
                url = f"{self.evolution_url}/reset"
                resp = requests.post(url, headers=self._get_headers(), timeout=10)

            return resp.status_code in (200, 201)
        except:
            return False

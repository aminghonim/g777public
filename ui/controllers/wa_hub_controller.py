"""
WhatsApp Hub Controller.
Decouples UI/API layer from the WAGateway service.
Renamed from cloud_hub_controller.py to reflect its actual purpose.
"""

import asyncio
from typing import Dict
from backend.cloud_service import cloud_service


class WAHubController:
    """
    Controller for WhatsApp Hub: connection refresh and AI assistant passthrough.
    """

    def __init__(self):
        self.state: Dict = {
            "is_connected": False,
            "chat_history": [],
        }

    def check_connection(self) -> bool:
        """Checks if connected to Evolution API."""
        is_con = cloud_service._verify_connection()
        self.state["is_connected"] = is_con
        return is_con

    async def refresh_connection(self) -> bool:
        """Refreshes connection state asynchronously."""
        is_con = await asyncio.to_thread(cloud_service._verify_connection)
        self.state["is_connected"] = is_con
        return is_con

    async def ask_ai(self, message: str) -> str:
        """Passes message to the AI fallback handler in WAGateway."""
        response = await asyncio.to_thread(cloud_service.ask_ai_cloud, message)
        self.state["chat_history"].append({"role": "user", "content": message})
        self.state["chat_history"].append({"role": "assistant", "content": response})
        return response

"""
WhatsApp Hub Controller
Manages WhatsApp connection status, QR authentication, and instance lifecycle.
"""

import logging
from typing import Dict, Any, Optional
from backend.wa_gateway import wa_gateway

logger = logging.getLogger(__name__)


class WAHubController:
    """
    Controller for managing WhatsApp connection hubs.
    """

    async def get_status(self, instance_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the current connection status of a WhatsApp instance.

        Args:
            instance_name: The name of the instance (defaults to main)

        Returns:
            Dict containing status and metadata.
        """
        try:
            state = await wa_gateway.get_connection_state(instance_name)
            info = await wa_gateway.get_instance_info(instance_name)
            
            return {
                "success": True,
                "status": state,
                "info": info
            }
        except (ConnectionError, RuntimeError, OSError) as e:
            logger.error("WA Hub Status Error: %s", e)
            return {
                "success": False,
                "error": str(e)
            }

    async def refresh_connection(self, instance_name: Optional[str] = None) -> bool:
        """
        Check if the connection is currently open.
        Compatible with older API routes.
        """
        result = await self.get_status(instance_name)
        return result.get("status") == "open"

    async def get_qr(self, instance_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a new QR code for WhatsApp authentication.

        Args:
            instance_name: The name of the instance

        Returns:
            Dict containing the QR code base64 or link.
        """
        try:
            qr_data = await wa_gateway.get_evolution_qr(instance_name)
            if qr_data:
                return {
                    "success": True,
                    "qr": qr_data
                }
            return {
                "success": False,
                "error": "Failed to generate QR code"
            }
        except (ConnectionError, RuntimeError, OSError, ValueError) as e:
            logger.error("WA Hub QR Error: %s", e)
            return {
                "success": False,
                "error": str(e)
            }

    async def logout(self, instance_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Logout and disconnect a WhatsApp instance.

        Args:
            instance_name: The name of the instance

        Returns:
            Success status.
        """
        try:
            success = await wa_gateway.logout_instance(instance_name)
            return {
                "success": success,
                "message": "Logged out successfully" if success else "Logout failed"
            }
        except (ConnectionError, RuntimeError, OSError) as e:
            logger.error("WA Hub Logout Error: %s", e)
            return {
                "success": False,
                "error": str(e)
            }

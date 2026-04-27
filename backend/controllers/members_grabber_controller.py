"""
Members Grabber Controller
Manages fetching WhatsApp groups and extracting members.
"""

import logging
from typing import Dict, Any, List, Optional
from backend.wa_gateway import wa_gateway

logger = logging.getLogger(__name__)


class MembersGrabberController:
    """
    Controller for managing member extraction from WhatsApp groups.
    """

    async def get_groups(self, instance_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch all available groups for a WhatsApp instance.

        Args:
            instance_name: The name of the instance

        Returns:
            Dict containing list of groups or an error.
        """
        try:
            groups = await wa_gateway.fetch_groups(instance_name)
            return {
                "success": True,
                "groups": groups
            }
        except (ConnectionError, RuntimeError, ValueError) as e:
            logger.error("Fetch Groups Error: %s", e)
            return {
                "success": False,
                "error": str(e)
            }

    async def extract_members(self, group_jid: str, instance_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract members from a specific WhatsApp group.

        Args:
            group_jid: The JID of the group
            instance_name: The name of the instance

        Returns:
            Dict containing list of members.
        """
        try:
            # First fetch group metadata to get members
            metadata = await wa_gateway.get_group_metadata(group_jid, instance_name)
            participants = metadata.get("participants", []) if metadata else []
            
            return {
                "success": True,
                "members": participants,
                "count": len(participants)
            }
        except (ConnectionError, RuntimeError, ValueError) as e:
            logger.error("Extract Members Error: %s", e)
            return {
                "success": False,
                "error": str(e)
            }

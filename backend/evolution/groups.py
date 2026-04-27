"""
Evolution API Groups Handler Module.
"""

import re
from typing import Any, Dict, List

import requests

from ..core.i18n import t
from .base import EvolutionBase


class GroupHandler(EvolutionBase):
    """
    Handles fetching groups, participants, joining via link, and polls.
    SaaS-Ready: Supports instance_name override per request.
    """

    def join_group_by_link(
        self, link: str, instance_name: str = None
    ) -> Dict[str, Any]:
        """Join a group via invite link."""
        try:
            instance = self._get_instance(instance_name)
            # Standard endpoint: /group/joinGroup/{instance}
            url = f"{self.evolution_url}/group/joinGroup/{instance}"
            payload = {"inviteCode": link.replace("https://chat.whatsapp.com/", "")}

            response = requests.post(
                url, json=payload, headers=self._get_headers(), timeout=30
            )
            if response.status_code in (200, 201):
                return {"success": True, "data": response.json()}
            return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_poll_to_group(
        self, jid: str, question: str, options: List[str], instance_name: str = None
    ) -> Dict[str, Any]:
        """Send a poll to a group."""
        try:
            instance = self._get_instance(instance_name)
            # Standard endpoint: /message/sendPoll/{instance}
            url = f"{self.evolution_url}/message/sendPoll/{instance}"
            payload = {
                "number": jid,  # Evolution uses 'number' for JID in message endpoints
                "name": question,
                "selectableCount": 1,
                "options": [{"pollName": opt} for opt in options],
            }

            response = requests.post(
                url, json=payload, headers=self._get_headers(), timeout=30
            )
            if response.status_code in (200, 201):
                return {"success": True, "data": response.json()}
            return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def fetch_all_groups(self, instance_name: str = None) -> Dict[str, Any]:
        """Fetch all groups current instance is part of."""
        try:
            instance = self._get_instance(instance_name)
            url = f"{self.evolution_url}/group/fetchAllGroups/{instance}?getParticipants=false"
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": t("cloud.errors.server_error", "Server Error: {msg}").format(
                    msg=str(e)
                ),
            }

    def fetch_group_participants(
        self, group_jid: str, instance_name: str = None
    ) -> List[Any]:
        """Fetch members of a specific group."""
        try:
            instance = self._get_instance(instance_name)
            group_jid = self._normalize_group_jid(group_jid)
            if not group_jid:
                return []

            url = f"{self.evolution_url}/group/findGroupInfos/{instance}?groupJid={group_jid}"
            response = requests.get(url, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []

    def _normalize_group_jid(self, group_jid: str) -> str:
        if not group_jid.endswith("@g.us"):
            if re.match(r"^[\d-]+$", group_jid):
                return f"{group_jid}@g.us"
            return ""
        return group_jid

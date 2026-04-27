import asyncio
from typing import Dict, List, Optional, Any
from backend.core.event_broker import event_broker


class CampaignState:
    """
    Multitenant Campaign State Tracker.
    Tracks active campaign status per user_id and broadcasts via EventBroker (Gap 2 Compliance).
    """

    def __init__(self):
        # Maps user_id -> campaign_data dict
        self._user_campaigns: Dict[str, Dict[str, Any]] = {}

    def _get_default_state(self):
        return {
            "is_running": False,
            "total": 0,
            "sent": 0,
            "failed": 0,
            "logs": [],
            "last_update": None,
        }

    def start_campaign(self, user_id: str, total: int):
        user_id = str(user_id)
        self._user_campaigns[user_id] = {
            "is_running": True,
            "total": total,
            "sent": 0,
            "failed": 0,
            "logs": ["🚀 Campaign Started"],
            "last_update": None,
        }
        self._notify(user_id)

    def update_progress(self, user_id: str, message: str, success: bool = True):
        user_id = str(user_id)
        if user_id not in self._user_campaigns:
            self._user_campaigns[user_id] = self._get_default_state()

        campaign = self._user_campaigns[user_id]
        campaign["logs"].append(message)

        if "Sent" in message:
            campaign["sent"] += 1
        elif "Error" in message or "Failed" in message:
            campaign["failed"] += 1

        self._notify(user_id)

    def finish_campaign(self, user_id: str, summary: str):
        user_id = str(user_id)
        if user_id in self._user_campaigns:
            campaign = self._user_campaigns[user_id]
            campaign["is_running"] = False
            campaign["logs"].append(summary)
            self._notify(user_id)

    def _notify(self, user_id: str):
        """Dispatches the state to the central EventBroker."""
        user_id = str(user_id)
        campaign_copy = self._user_campaigns.get(
            user_id, self._get_default_state()
        ).copy()

        # Notify central broker for the unified singleton SSE pipeline
        asyncio.create_task(
            event_broker.publish_campaign(campaign_copy, user_id=user_id)
        )


# Global Instance (Shared per process but partitioned by user_id)
campaign_state = CampaignState()

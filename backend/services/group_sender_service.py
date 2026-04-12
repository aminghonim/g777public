import logging
from typing import List, Dict, Any
from backend.evolution.groups import GroupHandler
from backend.database_manager import db_manager
from backend.core.event_broker import event_broker

logger = logging.getLogger(__name__)

class GroupSenderService:
    def __init__(self, instance_name: str):
        self.instance_name = instance_name
        self.handler = GroupHandler()

    def sync_groups(self) -> List[Dict[str, Any]]:
        """
        Fetches groups from Evolution API and normalizes them.
        """
        logger.info(f"Syncing groups for instance: {self.instance_name}")
        response = self.handler.fetch_all_groups(instance_name=self.instance_name)
        
        # Evolution API returns a list directly or a dict with data
        groups_data = response if isinstance(response, list) else response.get("data", [])
        
        normalized_groups = []
        for g in groups_data:
            normalized_groups.append({
                "id": g.get("id") or g.get("jid"),
                "name": g.get("subject") or g.get("name"),
                "member_count": len(g.get("participants", [])) if "participants" in g else 0
            })
        
        # Save to database
        try:
            db_manager.sync_groups_to_db(instance_name=self.instance_name, groups=normalized_groups)
            logger.info(f"Successfully synced {len(normalized_groups)} groups to DB")
        except Exception as e:
            logger.error(f"Failed to save groups to DB: {e}")

        return normalized_groups

    async def start_broadcast(self, group_ids: List[str], message: str, delay_min: int, delay_max: int, user_id: str = "global"):
        """
        Initiates the broadcast process with real-time SSE telemetry.
        """
        msg = f"🚀 Initiating broadcast to {len(group_ids)} groups for {self.instance_name}"
        logger.info(msg)
        await event_broker.publish_log(msg, level="SUCCESS", user_id=user_id)
        
        # Mocking the process for logic verification
        # Actual transmission would happen in a background loop
        return {"status": "started", "broadcast_id": "mock_id"}

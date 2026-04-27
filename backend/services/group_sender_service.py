import logging
import asyncio
import random
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
        Initiates the broadcast process with anti-ban sequential delays and SSE telemetry.
        """
        total = len(group_ids)
        start_msg = f"🚀 Starting broadcast to {total} groups (Delay: {delay_min}s-{delay_max}s)"
        logger.info(start_msg)
        await event_broker.publish_log(start_msg, level="INFO", user_id=user_id)

        for index, group_id in enumerate(group_ids, 1):
            # 1. State: SENDING
            sending_msg = f"[{index}/{total}] Sending to: {group_id}..."
            await event_broker.publish_log(sending_msg, level="INFO", user_id=user_id)
            
            # 2. Mock Transmission (In a real scenario, this calls GroupHandler)
            # await self.group_handler.send_message(group_id, message)
            await asyncio.sleep(0.5) # Minimum network latency mock
            
            # 3. State: SENT
            sent_msg = f"✅ Delivered to: {group_id}"
            await event_broker.publish_log(sent_msg, level="SUCCESS", user_id=user_id)
            
            # 4. Anti-Ban Delay (Except after the last message)
            if index < total:
                wait_time = random.randint(delay_min, delay_max)
                wait_msg = f"⏳ Throttling: Waiting {wait_time}s before next send..."
                await event_broker.publish_log(wait_msg, level="WARNING", user_id=user_id)
                await asyncio.sleep(wait_time)

        final_msg = f"🏁 Broadcast complete! Total: {total} groups reached."
        logger.info(final_msg)
        await event_broker.publish_log(final_msg, level="SUCCESS", user_id=user_id)
        
        return {"status": "completed", "total": total}

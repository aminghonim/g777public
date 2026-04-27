"""
Group Sender Controller
Manages group messaging campaigns and progress tracking with Redis persistence.
"""

import logging
import asyncio
import json
import time
from datetime import datetime
import pandas as pd
from typing import Dict, Any, List, Optional

from backend.wa_gateway import wa_gateway
from core.redis_client import redis_client
from backend.core.event_broker import event_broker

logger = logging.getLogger(__name__)


class GroupSenderController:
    """
    Controller for managing group messaging campaigns with Redis persistence.
    Supports Excel parsing and background execution via EventBroker.
    """

    def __init__(self) -> None:
        self._redis = redis_client
        self._local_fallback: Dict[str, Dict[str, Any]] = {}

    def get_sheets(self, file_path: str) -> List[str]:
        """Reads the Excel file and returns all sheet names."""
        try:
            excel_file = pd.ExcelFile(file_path)
            return [str(name) for name in excel_file.sheet_names]
        except (ValueError, KeyError, OSError) as e:
            logger.error("Failed to read Excel sheets: %s", e)
            return []

    def get_columns(self, file_path: str, sheet_name: str) -> List[str]:
        """Reads the Excel file and returns all column names for a sheet."""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=1)
            return [str(col) for col in df.columns.tolist()]
        except (ValueError, KeyError, OSError) as e:
            logger.error("Failed to read Excel columns: %s", e)
            return []

    def load_contacts(self, file_path: str, sheet_name: str) -> List[Dict[str, Any]]:
        """Parses Excel and returns a list of contact dictionaries."""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            # Ensure all columns are strings and handle empty values
            df = df.fillna("")
            return df.to_dict(orient="records")
        except (ValueError, KeyError, OSError) as e:
            logger.error("Failed to load contacts from Excel: %s", e)
            return []

    async def _save_campaign(self, user_id: str, campaign_id: str, data: Dict[str, Any]):
        """Save campaign state to Redis with user-specific isolation."""
        key = f"campaign:{user_id}:{campaign_id}"
        if self._redis:
            try:
                self._redis.set(key, json.dumps(data))
                # Expire after 7 days (604800 seconds)
                self._redis.expire(key, 604800)
            except (ConnectionError, ValueError, KeyError) as e:
                logger.error("Redis Save Error [%s]: %s", key, e)
                self._local_fallback[key] = data
        else:
            self._local_fallback[key] = data

    async def _load_campaign(self, user_id: str, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Load campaign state from Redis or local fallback."""
        key = f"campaign:{user_id}:{campaign_id}"
        if self._redis:
            try:
                data = self._redis.get(key)
                return json.loads(data) if data else None
            except (ConnectionError, ValueError, KeyError) as e:
                logger.error("Redis Load Error [%s]: %s", key, e)
                return self._local_fallback.get(key)
        return self._local_fallback.get(key)

    async def run_campaign(
        self,
        user_id: str,
        instance_name: str,
        contacts: List[Dict[str, Any]],
        message: List[str] | str,
        media_file: Optional[str] = None,
        group_link: Optional[str] = None,
        delay_min: int = 5,
        delay_max: int = 15,
        progress_callback: Optional[Any] = None,
    ) -> None:
        """
        Main entry point for running a messaging campaign. 
        Executed as a background task.
        """
        import random
        campaign_id = f"cmp_{int(time.time())}"
        
        state: Dict[str, Any] = {
            "status": "in_progress",
            "total": len(contacts),
            "sent": 0,
            "failed": 0,
            "start_time": datetime.now().isoformat(),
            "logs": ["🚀 Campaign Started"],
        }
        
        if group_link:
            state["logs"].append(f"🔗 Group Link provided: {group_link}")

        await self._save_campaign(user_id, campaign_id, state)
        await event_broker.publish_campaign(state, user_id=user_id)

        for index, contact in enumerate(contacts):
            phone = str(contact.get("phone") or contact.get("number") or "")
            if not phone:
                continue
                
            # Random delay for anti-ban
            current_delay = random.randint(delay_min, delay_max)
            
            try:
                msg = message[0] if isinstance(message, list) and message else message
                # Send message via wa_gateway
                success, response = await wa_gateway.send_whatsapp_message(
                    phone=phone,
                    message=msg,
                    media_path=media_file,
                    instance_name=instance_name
                )
                
                loaded_state = await self._load_campaign(user_id, campaign_id)
                if not loaded_state:
                    break
                state = loaded_state

                if success:
                    state["sent"] = state.get("sent", 0) + 1
                    log_entry = f"✅ Sent to {phone}"
                else:
                    state["failed"] = state.get("failed", 0) + 1
                    log_entry = f"❌ Failed to {phone}: {response}"
                
                if isinstance(state.get("logs"), list):
                    state["logs"].append(log_entry)
                
                # Update progress callback if provided (Legacy compatibility)
                if progress_callback:
                    progress_callback(user_id, log_entry, success)

                await self._save_campaign(user_id, campaign_id, state)
                await event_broker.publish_campaign(state, user_id=user_id)
                
                if index < len(contacts) - 1:
                    await asyncio.sleep(current_delay)
                    
            except (ConnectionError, RuntimeError, OSError) as e:
                logger.error("Surgical Process Error [%s]: %s", phone, e)
                loaded_state = await self._load_campaign(user_id, campaign_id)
                if loaded_state:
                    state = loaded_state
                    state["failed"] = state.get("failed", 0) + 1
                    if isinstance(state.get("logs"), list):
                        state["logs"].append(f"⚠️ System Error: {str(e)}")
                    await self._save_campaign(user_id, campaign_id, state)
                    await event_broker.publish_campaign(state, user_id=user_id)

        # Finalize
        loaded_state = await self._load_campaign(user_id, campaign_id)
        if loaded_state:
            state = loaded_state
            state["status"] = "completed"
            state["end_time"] = datetime.now().isoformat()
            await self._save_campaign(user_id, campaign_id, state)
            await event_broker.publish_campaign(state, user_id=user_id)
            logger.info("Campaign %s completed for User %s", campaign_id, user_id)

    async def get_progress(self, user_id: str, campaign_id: str) -> Dict[str, Any]:
        """Returns campaign state from Redis."""
        data = await self._load_campaign(user_id, campaign_id)
        if not data:
            return {"success": False, "error": "Campaign not found"}
        return {"success": True, **data}

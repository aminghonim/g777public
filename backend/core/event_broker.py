import asyncio
import json
import logging
from typing import Dict, Any, Set
from datetime import datetime

logger = logging.getLogger("g777.event_broker")


class EventBroker:
    """
    Central Singleton Event Hub (Gap 2 Compliance).
    Aggregates all system events (Logs, Status, Campaign, Telemetry)
    and broadcasts them to a unified SSE pipeline.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBroker, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.listeners: Set[asyncio.Queue] = set()
        self._initialized = True
        logger.info("Singleton EventBroker Initialized")

    def subscribe(self) -> asyncio.Queue:
        """Subscribe a new client to the stream."""
        queue = asyncio.Queue()
        self.listeners.add(queue)
        logger.debug(
            f"New stream client connected. Total listeners: {len(self.listeners)}"
        )
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        """Cleanly disconnect a client."""
        if queue in self.listeners:
            self.listeners.remove(queue)
            logger.debug(
                f"Stream client disconnected. Total listeners: {len(self.listeners)}"
            )

    async def publish(
        self, event_type: str, data: Dict[str, Any], user_id: str = "global"
    ):
        """
        Publishes a message to all connected listeners.
        Enforces a unified schema for easy multi-tenant client-side routing.
        """
        payload = {
            "type": event_type,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }

        message = json.dumps(payload)

        if not self.listeners:
            return

        # Broadcast to all queues
        # Use a list snapshot to prevent 'Set changed during iteration' errors
        for queue in list(self.listeners):
            try:
                queue.put_nowait(message)
            except Exception as e:
                logger.error(f"Failed to push message to listener: {e}")
                # Optional: Remove dead queues? Unsubscribe usually handles this via SSE disconnect.

    # --- Domain Specific Dispatchers ---

    async def publish_log(
        self, message: str, level: str = "INFO", user_id: str = "global"
    ):
        """Dispatch a system log entry."""
        await self.publish("LOG", {"message": message, "level": level}, user_id)

    async def publish_status(
        self, component: str, status: str, user_id: str = "global"
    ):
        """Dispatch a component status update (e.g. WhatsApp connection)."""
        await self.publish(
            "STATUS", {"component": component, "status": status}, user_id
        )

    async def publish_telemetry(self, cpu: float, ram: float):
        """Dispatch real-time hardware performance metrics."""
        await self.publish("TELEMETRY", {"cpu": cpu, "ram": ram})

    async def publish_quota(self, used: int, limit: int, user_id: str):
        """Dispatch user quota usage updates."""
        await self.publish("QUOTA", {"used": used, "limit": limit}, user_id)

    async def publish_campaign(self, campaign_data: Dict[str, Any], user_id: str):
        """Dispatch live campaign progress updates."""
        await self.publish("CAMPAIGN", campaign_data, user_id)

    async def publish_agent_step(
        self,
        step_type: str,
        reasoning: str,
        action: str,
        user_id: str = "global",
    ):
        """
        Dispatch AI Agent reasoning steps for real-time UI visibility.

        Args:
            step_type: Classification of the step
                       ('thinking', 'clicking', 'extracting', 'healing').
            reasoning: The agent's internal reasoning for this step.
            action: The concrete action performed (e.g. 'click button X').
            user_id: Tenant identifier for multi-tenant routing.
        """
        await self.publish(
            "AGENT_STEP",
            {
                "step_type": step_type,
                "reasoning": reasoning,
                "action": action,
            },
            user_id,
        )


# Global Singleton Instance
event_broker = EventBroker()

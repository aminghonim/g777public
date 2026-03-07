import asyncio
from typing import List, Dict
from backend.groups.auto_joiner import AutoJoiner


class AutoJoinerController:
    """UI controller wrapper for AutoJoiner.

    Usage: call `run_join(links, delay=60)` from UI code.
    """

    def __init__(self):
        self.state = {"is_joining": False}
        self.joiner = AutoJoiner()

    async def run_join(self, links: List[str], delay: int = 60) -> Dict[str, any]:
        if self.state["is_joining"]:
            return {"ok": False, "response": "already_running"}

        self.state["is_joining"] = True
        try:
            # Run the join operation in a thread to avoid blocking UI
            result = await asyncio.to_thread(self.joiner.join_groups, links, delay)
            return {"ok": True, "response": result}
        finally:
            self.state["is_joining"] = False

"""
Account Warmer Controller - Pure Backend Logic.
Manages asynchronous warming sessions between accounts.
"""

import asyncio
import logging
from typing import List, Dict, Any
from backend.warmer import AccountWarmer

# CNS Logging Compliance
logger = logging.getLogger(__name__)

class AccountWarmerController:
    """Manages the background tasks and logging for account warming."""

    def __init__(self):
        self.warmer = AccountWarmer()
        self._logs: List[str] = []
        self._running: bool = False
        self.state: Dict[str, Any] = {
            "is_running": False,
            "last_log": "Idle",
            "progress": 0
        }

    async def start_warming(self, phone1: str, phone2: str, count: int, delay: int) -> None:
        """Starts a warming cycle between accounts."""
        if self._running:
            logger.warning("Warming cycle already in progress.")
            return

        self._running = True
        self.state["is_running"] = True
        self._logs.append(f"Warming session initiated: {phone1} to {phone2}")
        
        try:
            for i in range(count):
                if not self._running:
                    logger.info("Warming loop interrupted manually.")
                    break
                
                msg = await self.warmer.generate_human_like_message()
                log_entry = f"[{i+1}/{count}] Message Sent: {msg}"
                self._logs.append(log_entry)
                self.state["last_log"] = log_entry
                self.state["progress"] = int(((i + 1) / count) * 100)
                
                logger.info(log_entry)
                
                if i < count - 1:
                    await asyncio.sleep(delay)

            self._logs.append("Warming cycle finished successfully.")
        except Exception as e:
            logger.error(f"Warming Fatal Error: {e}", exc_info=True)
            self._logs.append(f"Error: {str(e)}")
        finally:
            self._running = False
            self.state["is_running"] = False
            logger.info("Account warmer session finished.")

    def stop_warming(self) -> None:
        """Interrupts and stops the current warming cycle."""
        self._running = False
        self.state["is_running"] = False
        self._logs.append("Manual stop signal received. Halting cycle.")
        logger.warning("Account warming manually interrupted.")

    def get_logs(self) -> List[str]:
        """Retrieves session logs."""
        return self._logs[-50:] # Keep recent logs

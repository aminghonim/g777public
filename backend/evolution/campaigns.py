"""
WhatsApp Campaign Orchestrator.
Handles bulk messaging with smart delays and safety checks.
"""

import asyncio
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Tuple
from .messaging import MessagingHandler
from ..core.i18n import t


class CampaignHandler(MessagingHandler):
    """
    Orchestrates bulk messaging campaigns with smart delays and working hours.
    """

    async def run_smart_campaign(
        self,
        evolution_url: str,
        instance: str,
        headers: dict,
        numbers: List[str],
        message: str,
        media_file: Optional[str] = None,
        media_type: str = "image",
        delay_range: Tuple[int, int] = (5, 15),
        work_hours: Tuple[int, int] = (9, 22),
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:

        results = {"success": True, "details": []}
        total = len(numbers)

        for idx, phone in enumerate(numbers):
            # 1. Working Hours Check
            while not self._is_working_hour(work_hours[0], work_hours[1]):
                if progress_callback:
                    progress_callback(
                        t("sender.logs.sleeping_off_hours", "Sleeping (Off Hours)...")
                    )
                await asyncio.sleep(900)

            # 2. Send Logic
            try:
                if media_file:
                    success, resp = await asyncio.to_thread(
                        self._send_evolution_media,
                        evolution_url,
                        instance,
                        headers,
                        phone,
                        message,
                        media_file,
                        media_type,
                    )
                else:
                    success, resp = await asyncio.to_thread(
                        self._send_evolution_text,
                        evolution_url,
                        instance,
                        headers,
                        phone,
                        message,
                    )

                status = "sent" if success else "failed"
                results["details"].append(
                    {"phone": phone, "status": status, "response": resp}
                )

                if progress_callback:
                    progress_callback(
                        t(
                            "sender.logs.sent_progress", "Sent {curr}/{total} ({phone})"
                        ).format(curr=idx + 1, total=total, phone=phone)
                    )

            except asyncio.CancelledError:
                results["success"] = False
                break
            except Exception as e:
                # Log detailed error but continue campaign
                results["details"].append(
                    {"phone": phone, "status": "error", "error": str(e)}
                )

            # 3. Random Delay
            if idx < total - 1:
                wait_time = random.uniform(delay_range[0], delay_range[1])
                await asyncio.sleep(wait_time)

        return results

    def _is_working_hour(self, start: int, end: int) -> bool:
        current_hour = datetime.now().hour
        if start <= end:
            return start <= current_hour < end
        return current_hour >= start or current_hour < end

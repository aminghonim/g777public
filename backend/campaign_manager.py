"""
Campaign Manager Module.
Orchestrates bulk messaging campaigns with smart delays and working hour checks.
"""

import asyncio
import logging
import random
import traceback
from datetime import datetime
from typing import Optional, Callable

logger = logging.getLogger(__name__)
from backend.database_manager import db_manager
from backend.core.i18n import t


class CampaignManager:
    """
    Orchestrates bulk messaging campaigns.
    Decouples logic from the low-level provider.
    """

    def __init__(self, provider_service):
        """Initialize with a messaging provider service."""
        self.service = provider_service

    async def run_smart_campaign(
        self,
        numbers,
        message,
        user_id: str,
        instance_name: str = None,
        media_file=None,
        media_type=None,
        group_link=None,
        delay_min=5,
        delay_max=15,
        work_start=9,
        work_end=22,
        progress_callback: Optional[Callable] = None,
    ):
        """
        Smart Campaign Orchestrator with Multi-Message Rotation & SaaS Identity.
        """
        results = {"success": True, "details": []}
        total = len(numbers)
        from backend.campaign_state import campaign_state

        messages = [message] if isinstance(message, str) else message
        # Filter out empty messages
        messages = [m for m in messages if m and m.strip()]
        if not messages:
            messages = ["Default Message"]  # Safety fallback

        logger.info(
            "STARTING SMART CAMPAIGN (%s): %d contacts",
            user_id,
            total,
        )

        for idx, phone in enumerate(numbers):
            # 0. Quota Check (SAAS-013)
            quota = await asyncio.to_thread(db_manager.get_user_quota_info, user_id)
            if quota["message_count"] >= quota["daily_limit"]:
                logger.warning(
                    "Quota exceeded for user %s (%d/%d)",
                    user_id,
                    quota["message_count"],
                    quota["daily_limit"],
                )
                if progress_callback:
                    progress_callback(
                        user_id,
                        t("sender.logs.quota_exceeded", "Quota Exceeded!").format(
                            limit=quota["daily_limit"]
                        ),
                    )
                results["success"] = False
                break

            # 1. Working Hours Check
            while not self._is_working_hour(work_start, work_end):
                logger.info(
                    "Outside working hours (%d-%d). Sleeping for 15 mins...",
                    work_start,
                    work_end,
                )
                if progress_callback:
                    progress_callback(user_id, "Sleeping (Off Hours)...")
                await asyncio.sleep(900)

            # 2. Message Generation (MOVE INSIDE LOOP for individual rotation/replacement)
            current_message_template = random.choice(messages)

            # --- FEATURE: VARIABLE REPLACEMENT ---
            # Construct a contact dict if numbers is a list of strings
            # TODO: Future enhancement - Accept list of dicts in run_smart_campaign
            contact_data = {"phone": phone, "name": "Friend"}

            # Replace {name} or {phone}
            try:
                full_message = current_message_template.format(**contact_data)
            except KeyError:
                full_message = current_message_template

            if group_link:
                full_message += f"\n\n {group_link}"

            # 3. Send Logic
            try:
                # Use SaaS-aware cloud service
                if media_file:
                    success, resp = await asyncio.to_thread(
                        self.service.send_whatsapp_message,
                        phone,
                        full_message,
                        media_file,
                        media_type,
                        instance_name=instance_name,
                    )
                else:
                    success, resp = await asyncio.to_thread(
                        self.service.send_whatsapp_message,
                        phone,
                        full_message,
                        instance_name=instance_name,
                    )

                if success:
                    # SAAS-013: Atomic Accounting
                    await asyncio.to_thread(
                        db_manager.increment_daily_usage, user_id, "message_count"
                    )

                status = "sent" if success else "failed"
                results["details"].append(
                    {"phone": phone, "status": status, "response": resp}
                )

                if progress_callback:
                    progress_callback(user_id, f" Sent {idx+1}/{total} ({phone})")

            except asyncio.CancelledError:
                logger.warning("Campaign cancelled by user.")
                results["success"] = False
                break
            except Exception as e:
                logger.error("Error sending to %s: %s", phone, e)
                traceback.print_exc()
                results["details"].append(
                    {"phone": phone, "status": "error", "error": str(e)}
                )
                if progress_callback:
                    progress_callback(user_id, f" Error {phone}: {str(e)}")

            # 4. Smart Random Delay
            if idx < total - 1:
                wait_time = random.uniform(delay_min, delay_max)
                await asyncio.sleep(wait_time)

        # Final Report
        success_count = len(
            [
                x
                for x in results["details"]
                if str(x.get("status")) in ["success", "sent"]
            ]
        )
        summary_msg = f" Campaign Finished! Sent: {success_count}/{total}"
        if progress_callback:
            progress_callback(user_id, summary_msg)
            campaign_state.finish_campaign(user_id, summary_msg)

        return results

    def _is_working_hour(self, start, end):
        current_hour = datetime.now().hour
        if start <= end:
            return start <= current_hour < end
        else:
            return current_hour >= start or current_hour < end

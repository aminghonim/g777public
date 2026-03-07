import asyncio
from typing import List, Optional
from backend.cloud_service import cloud_service


class PollSenderController:
    """
    Stateless Controller for Poll Sender (SaaS Multitenant).
    """

    def __init__(self):
        # We keep local state for simple UI feedback,
        # but the heavy lifting is done with instance_name.
        self.state = {"is_sending": False}

    async def send_poll(
        self,
        question: str,
        options: List[str],
        instance_name: str,
        jid: Optional[str] = None,
    ):
        """Sends a poll to a specific group using user instance."""
        if self.state["is_sending"]:
            return {"ok": False, "error": "Busy"}

        self.state["is_sending"] = True
        try:
            # Protocol: If UI sends 'jid||question', we split it.
            target_jid = jid
            target_question = question

            if "||" in question and not jid:
                target_jid, target_question = question.split("||", 1)

            if not target_jid:
                return {"ok": False, "error": "missing_jid"}

            # Use SaaS-ready cloud service
            result = await asyncio.to_thread(
                cloud_service.send_poll_to_group,
                jid=target_jid,
                question=target_question,
                options=options,
                instance_name=instance_name,
            )
            return result
        finally:
            self.state["is_sending"] = False

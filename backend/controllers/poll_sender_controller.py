"""
Poll Sender Controller - Pure Backend Logic.
Manages distribution of WhatsApp polls to groups or contacts.
"""

import logging
from typing import List, Optional, Dict, Any
import pandas as pd
from backend.wa_gateway import wa_gateway

# CNS Logging Compliance
logger = logging.getLogger(__name__)

class PollSenderController:
    """Manages the lifecycle of poll distribution."""

    def __init__(self):
        self.state: Dict[str, Any] = {"is_sending": False}

    async def send_poll(self, question: str, options: List[str], 
                        excel_file: Optional[str] = None, 
                        instance_name: Optional[str] = None) -> None:
        """Sends a poll to targets, optionally extracted from an Excel file."""
        self.state["is_sending"] = True
        try:
            target_jids: List[str] = []
            
            if excel_file:
                # Load group JIDs from excel (expects JID in first column)
                df = pd.read_excel(excel_file)
                # Filter out empty rows and get JIDs
                target_jids = [str(jid) for jid in df.iloc[:, 0].dropna().tolist()]
            
            if not target_jids:
                logger.warning("Poll Sender: No valid JIDs found for distribution.")
                return

            # Batch send to targets
            for jid in target_jids:
                wa_gateway.send_poll_to_group(
                    jid=jid, 
                    question=question, 
                    options=options, 
                    instance_name=instance_name
                )
            
            logger.info("Poll successfully sent to %d targets using instance %s", len(target_jids), instance_name)
            
        except (ConnectionError, RuntimeError, OSError, ValueError) as e:
            logger.error("Poll Sender Error: %s", e)
            raise
        finally:
            self.state["is_sending"] = False

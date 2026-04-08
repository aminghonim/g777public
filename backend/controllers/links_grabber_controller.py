"""
Links Grabber Controller - Pure Backend Logic.
Manages WhatsApp group link searching and hunting state.
"""

import logging
from typing import List, Dict, Any
from backend.grabber.links_grabber import find_group_links

# CNS Logging Compliance
logger = logging.getLogger(__name__)

class LinksGrabberController:
    """Handles the hunting process for WhatsApp group links."""

    def __init__(self):
        self.state: Dict[str, Any] = {"results": [], "is_hunting": False}

    async def run_hunt(self, keyword: str, count: int) -> Dict[str, Any]:
        """Initiates the group link finding process."""
        self.state["is_hunting"] = True
        try:
            # Call the core grabber logic
            links = find_group_links(keyword, limit=count)
            self.state["results"] = links
            return {"status": "success", "found": len(links), "results": links}
        except (RuntimeError, OSError, ValueError) as e:
            logger.error("Links Grabber Error: %s", e)
            return {"status": "error", "message": str(e)}
        finally:
            self.state["is_hunting"] = False

    def clear_results(self) -> None:
        """Clears the stored results list."""
        self.state["results"] = []

import asyncio
from typing import List, Dict, Optional
from backend.group_finder import GroupFinder
from backend.grabber.links_grabber import find_group_links


class LinksGrabberController:
    """
    Controller for Links Grabber UI.
    Decouples UI from the GroupFinder selenium logic.
    """

    def __init__(self):
        self.state = {"results": [], "is_hunting": False}
        self.finder = GroupFinder()

    async def run_hunt(self, keyword: str, count: int) -> List[Dict]:
        """
        Runs the group finding process.
        count: Maximum number of groups to find (from UI slider)
        """
        if self.state["is_hunting"]:
            return []

        self.state["is_hunting"] = True
        try:
            # Prefer quick web search grabber; fallback to GroupFinder selenium if needed
            loop = asyncio.get_event_loop()
            links = await loop.run_in_executor(
                None, lambda: find_group_links(keyword, limit=count)
            )
            if not links:
                links = await loop.run_in_executor(
                    None,
                    lambda: self.finder.find_groups([keyword], max_links=count),
                )

            # Format results
            formatted = [
                {"name": f"Group Found ({i+1})", "link": link, "members": "Public"}
                for i, link in enumerate(links)
            ]

            self.state["results"] = formatted
            return formatted
        finally:
            self.state["is_hunting"] = False

    def clear_results(self):
        self.state["results"] = []

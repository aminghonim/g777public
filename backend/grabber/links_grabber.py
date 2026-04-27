"""
Links Grabber - Find public WhatsApp group invite links using web search

Features:
- Try `googlesearch` if available.
- Fallback to DuckDuckGo HTML scraping if network search lib missing.
- Validate and return unique invite links.
"""

from typing import List, Set
import re
import requests
import logging
import time

logger = logging.getLogger(__name__)


INVITE_RE = re.compile(r"https?://chat\.whatsapp\.com/[A-Za-z0-9_-]+")


def find_group_links(keyword: str, limit: int = 50, pause: float = 1.0) -> List[str]:
    """Search the web for WhatsApp group links matching `keyword`.

    Args:
        keyword: search term (e.g. "Football Fans").
        limit: maximum number of search results to consider.
        pause: seconds to wait between HTTP requests when scraping.

    Returns:
        List of unique invite URLs (strings).
    """
    query = f'site:chat.whatsapp.com "{keyword}"'
    found: Set[str] = set()

    # Prefer googlesearch if present (fast & mockable in tests)
    try:
        from googlesearch import search as gsearch  # type: ignore

        logger.debug("Using googlesearch for links")
        for url in gsearch(query, num_results=limit):
            if not url:
                continue
            for m in INVITE_RE.findall(url):
                found.add(m)
        return list(found)
    except Exception:
        logger.debug("googlesearch not available, falling back to DuckDuckGo scrape")

    # DuckDuckGo HTML interface (simple, no JS)
    try:
        dd_url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        resp = requests.get(dd_url, params=params, timeout=15)
        text = resp.text
        for m in INVITE_RE.findall(text):
            found.add(m)
        # If not enough results, try a naive Google result fetch attempt (may be blocked)
        if len(found) < 5:
            time.sleep(pause)
            # try plain HTTP GET on google search page (best-effort)
            try:
                g_resp = requests.get(
                    f"https://www.google.com/search?q={requests.utils.requote_uri(query)}",
                    timeout=10,
                )
                for m in INVITE_RE.findall(g_resp.text):
                    found.add(m)
            except Exception:
                logger.debug("Google fetch blocked or unavailable")

    except Exception as e:
        logger.exception("Search fallback failed: %s", e)

    return list(found)

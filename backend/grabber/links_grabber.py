"""
Links Grabber - Find public WhatsApp group invite links using web search

Features:
- Try `googlesearch` if available.
- Fallback to DuckDuckGo HTML scraping if network search lib missing.
- Validate and return unique invite links.
"""

from typing import List, Set
import re
import logging
import time
import requests

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
        from googlesearch import search as gsearch  # type: ignore # pylint: disable=import-error,import-outside-toplevel

        logger.debug("Using googlesearch for links")
        for url in gsearch(query, num_results=limit):
            if not url:
                continue
            for m in INVITE_RE.findall(url):
                found.add(m)
        return list(found)
    except Exception:  # pylint: disable=broad-exception-caught
        logger.debug("googlesearch not available, falling back to DuckDuckGo scrape")

    # DuckDuckGo HTML interface (simple, no JS)
    try:
        dd_url = "https://html.duckduckgo.com/html/"
        params = {"q": query}

        # Anti-Ban Jitter and Rotating User-Agents
        import random  # pylint: disable=import-outside-toplevel
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # pylint: disable=line-too-long
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",  # pylint: disable=line-too-long
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",  # pylint: disable=line-too-long
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        jitter = random.uniform(2.0, 5.0)
        logger.debug("Applying Jitter %.2fs before DDG fetch...", jitter)
        time.sleep(jitter)
        resp = requests.get(dd_url, params=params, headers=headers, timeout=15)
        text = resp.text
        for m in INVITE_RE.findall(text):
            found.add(m)
        # If not enough results, try a naive Google result fetch attempt (may be blocked)
        if len(found) < 5:
            time.sleep(pause + random.uniform(1.0, 3.0))
            # try plain HTTP GET on google search page (best-effort)
            try:
                g_resp = requests.get(
                    f"https://www.google.com/search?q={requests.utils.requote_uri(query)}",
                    timeout=10,
                )
                for m in INVITE_RE.findall(g_resp.text):
                    found.add(m)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.debug("Google fetch blocked or unavailable")

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.exception("Search fallback failed: %s", e)

    return list(found)

"""
Auto Joiner - safely join WhatsApp groups via Evolution API

Rules implemented:
- Validate invite link format.
- Use `EVOLUTION_API_URL` and optional `EVOLUTION_API_KEY` env vars.
- Delay between joins (default 60s), stop after 5 consecutive failures.
"""

from typing import List, Dict
import os
import re
import requests
import time
import logging

logger = logging.getLogger(__name__)


INVITE_RE = re.compile(r"https?://chat\.whatsapp\.com/[A-Za-z0-9_-]+")


class AutoJoiner:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or os.getenv("EVOLUTION_API_URL")
        self.api_key = api_key or os.getenv("EVOLUTION_API_KEY")

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["x-api-key"] = self.api_key
        return h

    def _validate(self, link: str) -> bool:
        return bool(INVITE_RE.match(link))

    def join_groups(
        self,
        links: List[str],
        delay: int = 60,
        stop_after_consecutive_failures: int = 5,
        dry_run: bool = True,
    ) -> Dict[str, any]:
        """Attempt to join a list of WhatsApp group invite links via Evolution API.

        Returns summary dict with keys: successes, failures (list of tuples (link, reason)).
        """
        if delay < 30:
            delay = 30

        summary = {"successes": [], "failures": []}
        consecutive_failures = 0

        for link in links:
            if consecutive_failures >= stop_after_consecutive_failures:
                logger.warning(
                    "Stopping after %s consecutive failures", consecutive_failures
                )
                break

            if not self._validate(link):
                reason = "invalid_link_format"
                summary["failures"].append((link, reason))
                consecutive_failures += 1
                continue

            payload = {"invite_link": link}
            if dry_run:
                logger.info("Dry-run enabled — skipping real join for %s", link)
                summary["successes"].append(link)
                consecutive_failures = 0
                # Skip performing the network request and sleeping in dry-run mode
                continue
            try:
                join_endpoint = f"{self.api_url.rstrip('/')}/groups/joinGroup"
                resp = requests.post(
                    join_endpoint, json=payload, headers=self._headers(), timeout=20
                )
                if resp.status_code in (200, 201):
                    summary["successes"].append(link)
                    consecutive_failures = 0
                    logger.info("Joined group: %s", link)
                else:
                    reason = f"http_{resp.status_code}"
                    # Try to extract error message
                    try:
                        reason = resp.json().get("error") or reason
                    except Exception:
                        pass
                    summary["failures"].append((link, reason))
                    consecutive_failures += 1
                    logger.warning("Failed to join %s : %s", link, reason)
            except Exception as e:
                summary["failures"].append((link, str(e)))
                consecutive_failures += 1
                logger.exception("Exception joining %s", link)

            # Delay between attempts
            time.sleep(delay)

        return summary

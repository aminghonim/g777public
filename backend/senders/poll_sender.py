"""
Poll Sender - construct and send poll messages via Evolution API

This module provides a small helper to build a poll payload and send it
through the Evolution API. It uses `EVOLUTION_API_URL` and optional
`EVOLUTION_API_KEY` environment variables.
"""

from typing import List, Dict
import os
import requests
import logging

logger = logging.getLogger(__name__)


def _headers(api_key: str = None) -> Dict[str, str]:
    h = {"Content-Type": "application/json"}
    if api_key:
        h["x-api-key"] = api_key
    return h


def send_poll(
    jid: str,
    question: str,
    options: List[str],
    api_url: str = None,
    api_key: str = None,
    timeout: int = 20,
) -> Dict[str, any]:
    """Send a poll to a group JID.

    Args:
        jid: group JID (e.g. 12345-678@g.us)
        question: poll question
        options: list of option strings (must be >=1)
        api_url: optional override for EVOLUTION_API_URL
        api_key: optional API key

    Returns:
        dict with 'ok' boolean and 'response' (server JSON or error).
    """
    if not options or len(options) < 1:
        return {"ok": False, "response": "empty_options"}

    base = api_url or os.getenv("EVOLUTION_API_URL")
    key = api_key or os.getenv("EVOLUTION_API_KEY")
    if not base:
        return {"ok": False, "response": "missing_api_url"}

    payload = {
        "jid": jid,
        "type": "poll",
        "poll": {
            "question": question,
            "options": [{"text": o} for o in options],
            "select": 1,
        },
    }

    # Try a dedicated endpoint first, then fallback to generic messages endpoint
    endpoints = ["/groups/sendPoll", "/messages/send_poll", "/messages"]
    headers = _headers(key)

    for ep in endpoints:
        url = f"{base.rstrip('/')}{ep}"
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
            if resp.status_code in (200, 201):
                try:
                    return {"ok": True, "response": resp.json()}
                except Exception:
                    return {"ok": True, "response": resp.text}
            else:
                # continue to next endpoint on non-200
                logger.debug("Poll send to %s returned %s", url, resp.status_code)
        except Exception as e:
            logger.debug("Poll send to %s failed: %s", url, e)
            continue

    return {"ok": False, "response": "all_endpoints_failed"}

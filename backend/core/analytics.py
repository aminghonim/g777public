"""
PostHog Analytics Client — Centralized Event Tracking.

Uses PostHog's REST API directly to avoid any SDK version conflicts.
All calls are fire-and-forget via httpx async to never block the main request path.
"""

import os
import logging
from typing import Dict, Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "")


def _is_enabled() -> bool:
    """Only send events when a valid API key is configured."""
    return bool(POSTHOG_API_KEY)


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=False,
)
async def track_event(
    distinct_id: str,
    event: str,
    properties: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Fire-and-forget async event tracking to PostHog.
    Uses tenacity with 2 retries to handle transient network issues
    without ever blocking the calling request.

    Args:
        distinct_id: The unique user/tenant identifier (Clerk user_id or instance_name).
        event: The event name (e.g. 'campaign_sent', 'login', 'crm_export').
        properties: Optional dictionary of event metadata.
    """
    if not _is_enabled():
        logger.debug("PostHog disabled — POSTHOG_API_KEY not set.")
        return

    payload = {
        "api_key": POSTHOG_API_KEY,
        "distinct_id": distinct_id,
        "event": event,
        "properties": properties or {},
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{POSTHOG_HOST}/capture/",
                json=payload,
            )
            if response.status_code >= 400:
                logger.warning(
                    "PostHog capture returned %s for event '%s'",
                    response.status_code,
                    event,
                )
    except httpx.RequestError as exc:
        logger.warning("PostHog network error for event '%s': %s", event, exc)


async def track_campaign_sent(
    user_id: str,
    instance_name: str,
    recipient_count: int,
) -> None:
    """Convenience wrapper for the most critical business event."""
    await track_event(
        distinct_id=user_id,
        event="campaign_sent",
        properties={
            "instance_name": instance_name,
            "recipient_count": recipient_count,
        },
    )


async def track_login(user_id: str, method: str = "clerk") -> None:
    """Track successful logins to measure DAU/MAU."""
    await track_event(
        distinct_id=user_id,
        event="login",
        properties={"method": method},
    )


async def track_crm_export(user_id: str, record_count: int) -> None:
    """Track CRM CSV exports to understand feature usage."""
    await track_event(
        distinct_id=user_id,
        event="crm_export",
        properties={"record_count": record_count},
    )

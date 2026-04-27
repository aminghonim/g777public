"""
Sentry Monitoring Router - AI Sentinel Webhook + Polling
=========================================================
Provides two mechanisms for error intake:
1. POST /monitoring/sentry-webhook  - Receives Sentry webhook payloads
2. POST /monitoring/poll-sentry     - Manually triggers a poll of recent Sentry issues

Both routes feed errors into the AI Sentinel for Gemini-powered analysis.
"""

import os
import hmac
import hashlib
import logging
import httpx
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services import sentinel_service

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])
logger = logging.getLogger("g777.monitoring")


class WebhookResponse(BaseModel):
    """Response model for webhook endpoint."""
    status: str
    message: str
    event_id: Optional[str] = None


class PollResponse(BaseModel):
    """Response model for polling endpoint."""
    status: str
    issues_found: int
    analyzed: int
    message: str


def _verify_sentry_signature(
    body: bytes, signature: str, secret: str
) -> bool:
    """
    Verify Sentry webhook HMAC-SHA256 signature.
    Prevents unauthorized payloads from triggering analysis.
    """
    expected = hmac.new(
        secret.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post(
    "/sentry-webhook",
    response_model=WebhookResponse,
    summary="Receive Sentry Webhook Events",
)
async def handle_sentry_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Receives error events from Sentry via webhook integration.
    Validates the HMAC signature, extracts the error payload,
    and queues it for AI analysis in the background.
    """
    body = await request.body()
    payload = await request.json()

    # Signature verification (optional if secret is configured)
    webhook_secret = os.getenv("SENTRY_WEBHOOK_SECRET", "")
    if webhook_secret:
        signature = request.headers.get("Sentry-Hook-Signature", "")
        if not _verify_sentry_signature(body, signature, webhook_secret):
            logger.warning(
                "[MONITORING] Invalid Sentry webhook signature. "
                "Rejecting payload."
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature",
            )

    # Check this is an error/issue event (not a test ping)
    resource = request.headers.get("Sentry-Hook-Resource", "")
    if resource == "installation":
        return WebhookResponse(
            status="ok",
            message="Installation hook acknowledged",
        )

    event_id = payload.get("event", {}).get("event_id", "unknown")
    logger.info(
        f"[MONITORING] Sentry webhook received. Event: {event_id}"
    )

    # Queue analysis in background so we respond to Sentry quickly
    background_tasks.add_task(sentinel_service.analyze_error, payload)

    return WebhookResponse(
        status="queued",
        message="Error event queued for AI analysis",
        event_id=event_id,
    )


@router.post(
    "/poll-sentry",
    response_model=PollResponse,
    summary="Poll Sentry for Recent Unresolved Issues",
)
async def poll_sentry_issues():
    """
    Manually triggers a poll of recent Sentry issues via the API.
    Useful when running on localhost without a public webhook URL.
    Fetches the 5 most recent unresolved issues and analyzes new ones.
    """
    sentry_dsn = os.getenv("SENTRY_DSN", "")
    sentry_auth_token = os.getenv("SENTRY_AUTH_TOKEN", "")

    if not sentry_dsn:
        raise HTTPException(
            status_code=503,
            detail="SENTRY_DSN not configured",
        )

    # Extract org and project from DSN
    # DSN format: https://<key>@o<org_id>.ingest.<region>.sentry.io/<project_id>
    # We use the Sentry API with an auth token instead
    sentry_org = os.getenv("SENTRY_ORG", "ai-opensky")
    sentry_project = os.getenv("SENTRY_PROJECT", "mcp")
    base_url = f"https://sentry.io/api/0/projects/{sentry_org}/{sentry_project}"

    if not sentry_auth_token:
        logger.warning(
            "[MONITORING] SENTRY_AUTH_TOKEN not set. "
            "Cannot poll Sentry API. "
            "Set it in .env to enable polling."
        )
        raise HTTPException(
            status_code=503,
            detail=(
                "SENTRY_AUTH_TOKEN not configured. "
                "Get it from: Settings > Auth Tokens in Sentry."
            ),
        )

    headers = {"Authorization": f"Bearer {sentry_auth_token}"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{base_url}/issues/",
                headers=headers,
                params={"query": "is:unresolved", "limit": 5},
            )
            resp.raise_for_status()
            issues = resp.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"[MONITORING] Sentry API error: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Sentry API returned {e.response.status_code}",
        )
    except Exception as e:
        logger.error(f"[MONITORING] Sentry API connection failed: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Cannot reach Sentry API: {e}",
        )

    analyzed_count = 0
    for issue in issues:
        # Fetch the latest event for this issue
        issue_id = issue.get("id", "")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                event_resp = await client.get(
                    f"{base_url}/issues/{issue_id}/events/latest/",
                    headers=headers,
                )
                event_resp.raise_for_status()
                event_data = event_resp.json()
        except Exception as e:
            logger.warning(
                f"[MONITORING] Cannot fetch event for issue {issue_id}: {e}"
            )
            continue

        # Build a payload similar to webhook format
        synthetic_payload = {
            "event": event_data,
            "project_slug": sentry_project,
            "org_slug": sentry_org,
        }

        result = await sentinel_service.analyze_error(synthetic_payload)
        if result:
            analyzed_count += 1

    return PollResponse(
        status="complete",
        issues_found=len(issues),
        analyzed=analyzed_count,
        message=(
            f"Polled {len(issues)} issues, "
            f"analyzed {analyzed_count} new errors."
        ),
    )

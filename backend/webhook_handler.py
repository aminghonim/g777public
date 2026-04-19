"""
G777 Webhook Handler - Enhanced Media Support
==============================================
Processes ALL types of WhatsApp messages: Text, Images, Audio, Video, Documents.
Flow: Baileys → Privacy → DB → AI → Reply + N8N Forwarding
"""

# Standard library
import asyncio
import hashlib
import hmac
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

# Third-party
import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

# Local / first-party
from .db_service import (
    create_conversation,
    create_customer,
    get_customer_by_phone,
    is_excluded,
    pause_bot_for_customer,
    save_message,
)

# Import manager for tenant-aware queries (Rule 12 Tenant Isolation)
from .database_manager import DatabaseManager
from .crm_intelligence import run_data_extraction
from .message_processor import extract_message_info

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
BOT_PAUSE_HOURS = int(os.getenv("BOT_PAUSE_ON_HUMAN_REPLY", "4"))

# ============================================================================
# SECURITY: M7 - WEBHOOK SIGNATURE VERIFICATION
# ============================================================================


async def verify_evolution_signature(request: Request) -> None:
    """
    FastAPI Dependency: enforces HMAC-SHA256 signature verification.

    WHY: Without this check any actor who knows the webhook URL can send
    arbitrary payloads, inject fake messages, and exhaust downstream
    resources (N8N, AI, DB). This is vulnerability M7.

    Algorithm:
        1. Read EVOLUTION_WEBHOOK_SECRET from environment (fail-closed if absent).
        2. Read the raw request body (bytes) — MUST happen before .json().
        3. Compute expected = "sha256=" + HMAC-SHA256(secret, body).
        4. Compare with x-evolution-signature header via hmac.compare_digest
           to prevent timing-oracle attacks (CWE-208 / OWASP).
        5. Reject with 403 on mismatch; 500 on missing configuration.
    """
    secret = os.getenv("EVOLUTION_WEBHOOK_SECRET", "")
    if not secret:
        # WHY: Fail-closed — a missing secret means the operator has not
        # configured the environment correctly. Allowing requests through
        # silently would defeat the entire security control.
        logger.error(
            "[Security] EVOLUTION_WEBHOOK_SECRET is not configured. "
            "Rejecting all webhook requests until the secret is set."
        )
        raise HTTPException(
            status_code=500,
            detail="Webhook secret not configured. Contact the system administrator.",
        )

    signature_header = request.headers.get("x-evolution-signature", "")
    body = await request.body()

    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()

    # WHY: compare_digest runs in constant time regardless of input length,
    # preventing an attacker from measuring response latency to infer the
    # correct HMAC byte-by-byte (CWE-208 timing attack).
    if not hmac.compare_digest(expected, signature_header):
        logger.warning(
            "[Security] Webhook signature MISMATCH — request rejected. "
            "Source IP: %s",
            request.client.host if request.client else "unknown",
        )
        raise HTTPException(status_code=403, detail="Invalid webhook signature.")


# ============================================================================
# MAIN WEBHOOK PROCESSOR
# ============================================================================


async def process_whatsapp_message(payload: Dict[str, Any]):
    """
    [Task] Main background task - Enhanced with full media support.

    Processing Steps:
    1. Extract message data (text + media)
    2. Validate and filter (ignore own messages, handle pause)
    3. Customer & Conversation management (Supabase)
    4. Save user message
    5. Trigger CRM intelligence
    6. Generate and send AI response (if not paused)
    7. Forward to N8N for advanced processing
    """
    try:
        # ==================== STEP 1: EXTRACT MESSAGE ====================
        # [Task] CRITICAL: Unpack 5 values (added media_metadata)
        message_text, remote_jid, is_from_me, media_type, media_metadata = (
            extract_message_info(payload)
        )

        # ==================== STEP 2: VALIDATION ====================

        # 2.1 Ignore own messages (prevent loop)
        if is_from_me:
            if remote_jid:
                phone = remote_jid.split("@")[0]
                logger.info(
                    f"[User] Human agent replied to {phone}. Pausing bot for {BOT_PAUSE_HOURS}h"
                )
                pause_bot_for_customer(phone, hours=BOT_PAUSE_HOURS)
            return

        # 2.2 Validate we have either text OR media
        if not remote_jid:
            logger.warning("[Warn] No remoteJid found, skipping message")
            return

        if not message_text and not media_type:
            logger.warning(f"[Warn] Empty message (no text or media) from {remote_jid}")
            return

        # Extract phone number
        phone = remote_jid.split("@")[0]

        # Log received message (PII-safe: redact phone and truncate content)
        preview = message_text[:30] if message_text else f"[{media_type}]"
        redacted_phone = phone[:4] + "****" + phone[-2:] if len(phone) > 6 else "***"
        logger.info(
            f"[Inbound] Processing | From: {redacted_phone} | Content: {preview} | Media: {media_type or 'none'}"
        )

        # ==================== STEP 3: CUSTOMER MANAGEMENT ====================
        customer = get_customer_by_phone(phone)

        if not customer:
            cust_id = create_customer(phone, ctype="lead")
            logger.info(f"[New] New customer created: {phone} (ID: {cust_id})")
        else:
            cust_id = customer["id"]
            logger.info(f"[User] Existing customer: {phone} (ID: {cust_id})")

        # ==================== STEP 4: CONVERSATION MANAGEMENT ====================
        conv_id = create_conversation(cust_id, phone)

        # ==================== STEP 5: SAVE USER MESSAGE ====================
        # Include media type in message for context
        full_message = message_text
        if media_type and not message_text:
            full_message = f"[{media_type.upper()}]"
        elif media_type and message_text:
            full_message = f"[{media_type.upper()}] {message_text}"

        save_message(conv_id, cust_id, "user", full_message)
        logger.info(f"[DB] User message saved to DB (conv: {conv_id})")

        # ==================== STEP 6: TRIGGER CRM INTELLIGENCE ====================
        asyncio.create_task(run_data_extraction(phone, conv_id))

        # ==================== STEP 7: CHECK EXCLUSION/PAUSE ====================
        if is_excluded(phone):
            logger.info(f"[Pause] Bot is PAUSED for {phone}. Skipping forwarding.")
            return

        # ==================== STEP 8: GENERATE AI RESPONSE (DISABLED - N8N HANDLES THIS) ====================
        # [DISABLED] DISABLED: Python Backend no longer generates AI responses.
        # N8N is now the primary brain for all AI replies.
        # The code below is kept for reference but commented out.

        # try:
        #     # Get conversation history
        #     history_text = get_conversation_history(conv_id, limit=10)
        #
        #     # Generate response (enhanced with media context)
        #     final_response = await process_ai_response(
        #         message_text=message_text,
        #         phone=phone,
        #         history_text=history_text,
        #         media_type=media_type  # Pass media context to AI
        #     )
        #
        #     if final_response:
        #         logger.info(f"[AI] AI Response ready: {final_response[:80]}...")
        #
        #         # Send via Baileys (use original remote_jid for @lid support)
        #         result = await baileys_client.send_message(remote_jid, final_response)
        #
        #         if result and result.get('success'):
        #             # Save bot response to DB
        #             save_message(conv_id, None, 'assistant', final_response)
        #             logger.info(f"[OK] Message sent successfully to {phone}")
        #         else:
        #             logger.error(f"[ERR] Failed to send message to {phone}: {result}")
        #     else:
        #         logger.warning(f"[Warn] Empty AI response for {phone}")
        #
        # except Exception as ai_err:
        #     logger.error(f"[ERR] AI Generation/Send failed: {ai_err}", exc_info=True)

        logger.info(
            f"[Skip] Skipping Python AI reply. N8N will handle response for {phone}."
        )

        # ==================== STEP 9: FORWARD TO N8N (PRIMARY BRAIN) ====================
        if N8N_WEBHOOK_URL:
            logger.info(f"Forwarding to N8N (Primary AI Brain) for {phone}")
            asyncio.create_task(
                forward_to_n8n(N8N_WEBHOOK_URL, payload, media_type, media_metadata)
            )
        else:
            logger.error(
                "[Warn] N8N_WEBHOOK_URL not configured! No AI reply will be sent."
            )

    except Exception as e:
        logger.error(
            f"[ERR] Critical error in process_whatsapp_message: {e}", exc_info=True
        )


# ============================================================================
# N8N FORWARDING
# ============================================================================


async def forward_to_n8n(
    url: str, payload: dict, media_type: str = None, media_metadata: dict = None
):
    """
    Forward message to N8N with enhanced metadata.

    N8N will handle:
    - Audio transcription (Gemini)
    - Image analysis (Gemini)
    - Video processing
    - Document extraction
    """
    try:
        # Extract data for N8N mapping
        message_text, remote_jid, is_from_me, _, _ = extract_message_info(payload)
        phone = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid
        data = payload.get("data", {})

        # Build enhanced payload for N8N
        n8n_payload = {
            # Basic info
            "phone": phone,
            "chatId": remote_jid,
            "message": message_text,
            "fromMe": is_from_me,
            "pushName": data.get("pushName", "Customer"),
            "instanceId": data.get("instanceId", "G777"),
            # Media info (enhanced)
            "mediaType": media_type,
            "mediaMetadata": media_metadata,
            "hasMedia": media_type is not None,
            # Raw data (for N8N Switch node)
            "data": data,  # 👈 Critical for: body.data.key.fromMe
            "body": payload,  # Full payload for compatibility
            # Timestamp
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"Forwarding to N8N | Target: {phone} | Media: {media_type or 'none'}"
        )

        headers = {
            "User-Agent": "G777-Backend/2.0",
            "Content-Type": "application/json",
            "X-Media-Type": media_type or "text",
        }

        async with httpx.AsyncClient(follow_redirects=True, verify=True) as client:
            response = await client.post(
                url, json=n8n_payload, headers=headers, timeout=15.0
            )

            if response.status_code == 200:
                logger.info(f"[OK] N8N accepted: {response.status_code}")
            else:
                logger.warning(
                    f"[Warn] N8N response: {response.status_code} | {response.text[:100]}"
                )

            return response

    except httpx.TimeoutException:
        logger.error("N8N Timeout after 15s")
    except Exception as e:
        logger.error("[ERR] N8N Forwarding Error: %s", e, exc_info=True)

    return None


# ============================================================================
# API ENDPOINTS
# ============================================================================


@router.get("/webhook/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "g777-backend",
        "version": "2.0",
        "features": [
            "text_messages",
            "image_support",
            "audio_support",
            "video_support",
            "document_support",
            "ai_humanization",
            "crm_intelligence",
            "n8n_integration",
        ],
    }


@router.post("/webhook/whatsapp", dependencies=[Depends(verify_evolution_signature)])
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    [Task] Main webhook entry point for Evolution API v2.

    Handles all message types from WhatsApp via Baileys service.
    """
    try:
        payload = await request.json()

        # Log raw webhook (truncated for security)
        payload_preview = json.dumps(payload)[:500]
        logger.info(
            f"INCOMING WEBHOOK RECEIVED | Event: {payload.get('event')} | Preview: {payload_preview}"
        )

        # Process in background
        background_tasks.add_task(process_whatsapp_message, payload)

        return {"status": "processing", "timestamp": datetime.now().isoformat()}

    except json.JSONDecodeError:
        logger.error("[ERR] Invalid JSON payload")
        return JSONResponse(
            status_code=400, content={"status": "error", "message": "Invalid JSON"}
        )
    except Exception as e:
        logger.error(f"[ERR] Webhook endpoint error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"status": "error", "message": str(e)}
        )


# ---------------------------------------------------------------------------
# Evolution-specific webhook (tenant‑aware lead insertion)
# ---------------------------------------------------------------------------

@router.post("/api/webhook/evolution", dependencies=[Depends(verify_evolution_signature)])
async def evolution_webhook(request: Request):
    """Handle incoming text messages from Evolution API.

    1. Expect a JSON payload containing **sender_number**,
       **instance_name** and **message_type**.
    2. Only take action on text messages; ignore others gracefully.
    3. Consult ``DatabaseManager`` with ``instance_name`` as the
       tenant/user identifier.
    4. If the phone number does not exist, upsert a new **lead**.

    Returns a simple status dict or error details.
    """
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        logger.error("[ERR] Invalid JSON payload for evolution webhook")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid JSON"},
        )

    sender = None
    instance = payload.get("instance")
    event = payload.get("event")

    if event != "messages.upsert":
        logger.info(f"[Info] Ignoring non-upsert event: {event}")
        return {"status": "ignored", "reason": f"event {event}"}

    data = payload.get("data", {})
    key = data.get("key", {})
    from_me = key.get("fromMe", False)

    if from_me:
        return {"status": "ignored", "reason": "own_message"}

    remote_jid = key.get("remoteJid", "")
    if remote_jid and "@s.whatsapp.net" in remote_jid:
        sender = remote_jid.split("@")[0]

    if not sender or not instance:
        logger.error("[ERR] Missing sender or instance in payload")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Missing required fields",
            },
        )


    try:
        db = DatabaseManager()
        existing = db.get_customer_by_phone(sender, instance)
        if not existing:
            # insert as lead (customer_type is handled by upsert logic)
            db.upsert_customer(phone=sender, user_id=instance)
            logger.info(f"[DB] New lead created: {sender} @ {instance}")
        else:
            logger.info(f"[DB] Customer already exists: {sender} @ {instance}")
    except Exception as e:
        logger.error(f"[ERR] Evolution DB operation failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Database failure"},
        )

    return {"status": "ok"}


# ============================================================================
# ADDITIONAL ENDPOINTS (Optional - for manual testing)
# ============================================================================


@router.post("/webhook/test")
async def test_webhook(request: Request):
    """Test endpoint to validate message extraction."""
    payload = await request.json()

    try:
        message_text, remote_jid, is_from_me, media_type, media_metadata = (
            extract_message_info(payload)
        )

        return {
            "success": True,
            "extracted": {
                "message_text": message_text,
                "remote_jid": remote_jid,
                "is_from_me": is_from_me,
                "media_type": media_type,
                "media_metadata": media_metadata,
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

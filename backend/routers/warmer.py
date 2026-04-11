"""
Account Warmer Router - FR-013, FR-014
Automated message sending with configurable delays and limits.
Ensures data isolation via user_id from JWT.
"""

import asyncio
import logging
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.database_manager import db_manager
from core.dependencies import get_current_user
from backend.core.event_broker import event_broker
from backend.core.evolution_manager import evolution_manager
from backend.cloud_service import G777CloudService
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random,
    retry_if_exception_type,
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/warmer", tags=["Account Warmer"])


# Request/Response Models
class WarmerConfigRequest(BaseModel):
    """FR-013: Account warmer configuration request."""
    name: str
    delay_interval_seconds: int = 30
    message_limit_per_day: int = 100


class WarmerConfigResponse(BaseModel):
    """Account warmer configuration response."""
    id: str
    user_id: str
    name: str
    delay_interval_seconds: int
    message_limit_per_day: int
    is_active: bool
    created_at: str
    updated_at: str


class WarmerActionRequest(BaseModel):
    """Start/stop warmer action."""
    config_id: str


# Background task tracking
_active_warmers: Dict[str, asyncio.Task] = {}


@router.post("/config", response_model=WarmerConfigResponse, status_code=201)
async def create_warmer_config(
    request: WarmerConfigRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> WarmerConfigResponse:
    """
    FR-013: Create or update an account warmer configuration.
    
    Requires authentication (JWT token).
    Returns the created/updated warmer configuration.
    """
    user_id = current_user.get("user_id") or current_user.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to extract user_id from token",
        )

    try:
        config_id = db_manager.create_warmer_config(
            user_id=user_id,
            name=request.name,
            delay_interval_seconds=request.delay_interval_seconds,
            message_limit_per_day=request.message_limit_per_day,
        )

        config = db_manager.get_warmer_config(user_id, config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created configuration",
            )

        return WarmerConfigResponse(**config)

    except Exception as e:
        logger.error(f"Error creating warmer config for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create warmer configuration",
        )


@router.get("/configs", response_model=List[WarmerConfigResponse])
async def get_warmer_configs(
    is_active: bool = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[WarmerConfigResponse]:
    """
    FR-013: Retrieve all warmer configurations for the authenticated user.
    
    Optional filter: is_active (true/false)
    """
    user_id = current_user.get("user_id") or current_user.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to extract user_id from token",
        )

    try:
        configs = db_manager.get_warmer_configs_by_user(user_id, is_active)
        return [WarmerConfigResponse(**config) for config in configs]

    except Exception as e:
        logger.error(f"Error fetching warmer configs for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve warmer configurations",
        )


@router.post("/start", status_code=200)
async def start_warmer(
    request: WarmerActionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    FR-014: Start account warmer automation.
    
    Begins the background task for automated message sending.
    Respects delay_interval_seconds and message_limit_per_day.
    """
    user_id = current_user.get("user_id") or current_user.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to extract user_id from token",
        )

    try:
        # Verify config exists and is owned by this user
        config = db_manager.get_warmer_config(user_id, request.config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warmer configuration not found",
            )

        # Update status to active
        success = db_manager.update_warmer_config_status(
            user_id, request.config_id, is_active=True
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to activate warmer",
            )

        # Start background task for this warmer
        task_key = f"{user_id}:{request.config_id}"
        if task_key not in _active_warmers or _active_warmers[task_key].done():
            task = asyncio.create_task(_warmer_loop(user_id, request.config_id, config))
            _active_warmers[task_key] = task
            logger.info(f"Started warmer task for {task_key}")

        return {
            "status": "started",
            "config_id": request.config_id,
            "message": "Warmer automation started",
            "started_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting warmer for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start warmer automation",
        )


@router.post("/stop", status_code=200)
async def stop_warmer(
    request: WarmerActionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    FR-014: Stop account warmer automation.
    
    Halts the background task for message sending.
    """
    user_id = current_user.get("user_id") or current_user.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to extract user_id from token",
        )

    try:
        # Verify config exists and is owned by this user
        config = db_manager.get_warmer_config(user_id, request.config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warmer configuration not found",
            )

        # Update status to inactive
        success = db_manager.update_warmer_config_status(
            user_id, request.config_id, is_active=False
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate warmer",
            )

        # Cancel background task if running
        task_key = f"{user_id}:{request.config_id}"
        if task_key in _active_warmers:
            task = _active_warmers[task_key]
            if not task.done():
                task.cancel()
                logger.info(f"Stopped warmer task for {task_key}")
            del _active_warmers[task_key]

        return {
            "status": "stopped",
            "config_id": request.config_id,
            "message": "Warmer automation stopped",
            "stopped_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping warmer for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop warmer automation",
        )


@router.get("/status/{config_id}")
async def get_warmer_status(
    config_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    FR-014: Get current status of a warmer configuration.
    """
    user_id = current_user.get("user_id") or current_user.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to extract user_id from token",
        )

    try:
        config = db_manager.get_warmer_config(user_id, config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warmer configuration not found",
            )

        task_key = f"{user_id}:{config_id}"
        is_running = task_key in _active_warmers and not _active_warmers[task_key].done()

        return {
            "config_id": config_id,
            "is_active": config["is_active"],
            "is_running": is_running,
            "name": config["name"],
            "delay_interval_seconds": config["delay_interval_seconds"],
            "message_limit_per_day": config["message_limit_per_day"],
            "last_updated": config["updated_at"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting warmer status for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve warmer status",
        )


async def _warmer_loop(user_id: str, config_id: str, config: Dict) -> None:
    """
    Background coroutine for account warmer automation.
    
    Polls for queued messages and sends them at configured intervals.
    Respects daily message limits.
    """
    delay_interval = config.get("delay_interval_seconds", 30)
    message_limit = config.get("message_limit_per_day", 100)
    
    logger.info(
        f"Starting warmer loop for {user_id}:{config_id} "
        f"(interval={delay_interval}s, limit={message_limit}/day)"
    )

    try:
        sent_today = 0
        reset_time = datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=1)

        while True:
            # Check if we've exceeded daily limit
            if sent_today >= message_limit:
                seconds_until_reset = (reset_time - datetime.utcnow()).total_seconds()
                if seconds_until_reset > 0:
                    logger.info(
                        f"Daily limit reached for {user_id}. "
                        f"Will resume in {int(seconds_until_reset)}s"
                    )
                    await asyncio.sleep(min(seconds_until_reset, delay_interval))
                    # Reset counter
                    sent_today = 0
                    reset_time = datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=1)
                    continue

            # Fetch queued messages for this warmer config
            messages = db_manager.get_warmer_messages(user_id, limit=message_limit - sent_today)
            if not messages:
                logger.debug(f"No queued warmer messages for {user_id}:{config_id}")
                await asyncio.sleep(delay_interval)
                continue

            # Prepare cloud service and get user's instance(s)
            cloud = G777CloudService()
            instances = []
            inst = evolution_manager._get_user_instance(user_id)
            if inst:
                instances.append(inst)
            # fallback to default if none
            if not instances:
                instances = [None]

            # send each message with retry logic
            for msg in messages:
                msg_id = msg.get("id")
                phone = msg.get("phone")
                text = msg.get("message")
                # choose instance by round robin
                chosen_instance = instances[sent_today % len(instances)]

                @retry(
                    stop=stop_after_attempt(3),
                    wait=wait_random(min=1, max=5),
                    retry=retry_if_exception_type(Exception),
                )
                async def attempt_send():
                    success, resp = await asyncio.to_thread(
                        cloud.send_whatsapp_message,
                        phone,
                        text,
                        instance_name=chosen_instance,
                    )
                    if not success:
                        raise Exception(resp)
                    return resp

                try:
                    await attempt_send()
                    sent_today += 1
                    await event_broker.publish_log(
                        f"Warmer sent to {phone}", user_id=user_id
                    )
                    # remove from queue to prevent duplicate sends
                    try:
                        db_manager.delete_warmer_message(msg_id)
                    except Exception:
                        logger.exception("failed to remove message from warmer pool")
                except Exception as send_exc:
                    logger.error(
                        f"Warmer message failed for {user_id} to {phone}: {send_exc}"
                    )
                    # human-like jitter before retry loop continues
                    await asyncio.sleep(delay_interval + random.uniform(1, 3))
                    continue

            await asyncio.sleep(delay_interval)

    except asyncio.CancelledError:
        logger.info(f"Warmer loop cancelled for {user_id}:{config_id}")
    except Exception as e:
        logger.error(f"Error in warmer loop for {user_id}:{config_id}: {e}")
        # Optionally notify user or pause warmer
        try:
            db_manager.update_warmer_config_status(user_id, config_id, is_active=False)
        except Exception as update_err:
            logger.error(f"Failed to pause warmer on error: {update_err}")

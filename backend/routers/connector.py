from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging
import time

from backend.wa_gateway import wa_gateway as cloud_service
from backend.grabber.links_grabber import find_group_links

router = APIRouter()
logger = logging.getLogger(__name__)


# --- Models ---
class LinkSearchRequest(BaseModel):
    keyword: str
    limit: int = 50


class JoinRequest(BaseModel):
    links: List[str]
    delay: int = 60
    dry_run: bool = True  # Default to Safe Mode


class PollRequest(BaseModel):
    jid: str
    question: str
    options: List[str]


@router.post("/join_groups")
async def auto_join_groups(
    req: JoinRequest,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Start a background task to join groups.
    SaaS-Ready: Uses user's specific WhatsApp instance.
    """
    instance_name = user.get("instance_name")

    # Define bg task with captured instance context
    def _run_joiner_task(links: List[str], delay: int, dry_run: bool, instance: str):
        summary = {"successes": [], "failures": []}
        for link in links:
            if dry_run:
                logger.info(f"[DRY-RUN] Joined {link} via {instance}")
                summary["successes"].append(link)
                continue

            # Use CloudService with SaaS override
            res = cloud_service.join_group_by_link(link, instance_name=instance)
            if res.get("success"):
                summary["successes"].append(link)
            else:
                summary["failures"].append((link, res.get("error")))

            time.sleep(max(5, delay))  # Minimum 5s delay

        logger.info(f"SaaS Joiner Task ({instance}): {summary}")
        # TODO: Save to DB (Task SAAS-011)

    background_tasks.add_task(
        _run_joiner_task, req.links, req.delay, req.dry_run, instance_name
    )

    return {
        "status": "started",
        "message": f"Joining {len(req.links)} groups via {instance_name}",
        "instance": instance_name,
    }


@router.post("/send_poll")
async def send_group_poll(
    req: PollRequest, user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a poll to a specific group.
    SaaS-Ready: Uses user's specific WhatsApp instance.
    """
    instance_name = user.get("instance_name")

    result = cloud_service.send_poll_to_group(
        req.jid, req.question, req.options, instance_name=instance_name
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result


@router.get("/status")
async def get_instance_status(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get the connection state of the user's WhatsApp instance.
    """
    instance_name = user.get("instance_name")
    status_data = cloud_service.get_connection_state(instance_name=instance_name)

    # Enrich with local SaaS metadata if needed
    status_data["user"] = user.get("username")
    status_data["instance_name"] = instance_name

    # Normalize 'is_connected' for Frontend
    inst = status_data.get("instance", {})
    state = inst.get("state")
    status_data["is_connected"] = state == "open" or state == "connected"
    status_data["details"] = inst

    return status_data


@router.post("/grab_links")
async def grab_whatsapp_links(
    req: LinkSearchRequest, user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Search the web for WhatsApp group links.
    """
    logger.info("User %s searching for links: %s", user.get("username"), req.keyword)
    try:
        links = find_group_links(req.keyword, limit=req.limit)
        return {"success": True, "links": links, "count": len(links)}
    except Exception as e:
        logger.error("Link grab failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/logout")
async def logout_instance(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Disconnect/Logout the user's WhatsApp instance.
    """
    instance_name = user.get("instance_name")
    success = cloud_service.logout_instance(instance_name=instance_name)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to logout instance")

    return {"status": "success", "message": f"Instance {instance_name} logged out"}

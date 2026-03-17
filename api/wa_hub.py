"""
WhatsApp Hub API Router.
Provides endpoints for WhatsApp connection status, QR codes, and AI chat.
Renamed from cloud_hub.py to reflect its actual purpose: local WA connection management.
"""

import asyncio
from fastapi import APIRouter, Body
from ui.controllers.wa_hub_controller import WAHubController
from backend.cloud_service import cloud_service

router = APIRouter(prefix="/api/wa-hub", tags=["WhatsApp Hub"])
controller = WAHubController()


@router.get("/status")
async def get_status() -> dict:
    """Checks connection status to Evolution API."""
    is_connected = await controller.refresh_connection()
    state = {}
    if is_connected:
        state = await asyncio.to_thread(cloud_service.get_connection_state)
    return {"is_connected": is_connected, "details": state}


@router.get("/qr")
async def get_qr() -> dict:
    """Fetches QR Code for WhatsApp linking."""
    result = await asyncio.to_thread(cloud_service.get_evolution_qr)
    return result


@router.get("/pairing-code")
async def get_pairing_code(phone: str) -> dict:
    """Fetches 8-digit Pairing Code for WhatsApp linking."""
    result = await asyncio.to_thread(cloud_service.get_pairing_code, phone)
    return result


@router.post("/logout")
async def logout() -> dict:
    """Disconnects and logs out of WhatsApp."""
    success = await asyncio.to_thread(cloud_service.logout_instance)
    return {"success": success}


@router.post("/chat")
async def chat_with_ai(message: str = Body(..., embed=True)) -> dict:
    """Sends a message to the AI assistant."""
    response = await controller.ask_ai(message)
    return {"response": response, "history": controller.state["chat_history"]}

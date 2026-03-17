"""
backend.senders package

Contains specialized sender utilities (poll, media, etc.).
WhatsAppSender is located in backend/whatsapp_sender.py (canonical module).
Import it directly: from backend.whatsapp_sender import WhatsAppSender
"""

from backend.senders.poll_sender import send_poll  # noqa: F401

__all__ = ["send_poll"]

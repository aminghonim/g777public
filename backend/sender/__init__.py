"""
backend.sender package — COMPATIBILITY SHIM

The canonical WhatsAppSender module is now: backend.whatsapp_sender
This shim re-exports WhatsAppSender so that existing imports continue to work
during the migration period.

MIGRATION PATH:
  OLD (deprecated): from backend.sender import WhatsAppSender
  NEW (canonical):  from backend.whatsapp_sender import WhatsAppSender
"""

from backend.whatsapp_sender import WhatsAppSender  # noqa: F401
from backend.cloud_service import AzureCloudService  # noqa: F401

__all__ = ["WhatsAppSender", "AzureCloudService"]

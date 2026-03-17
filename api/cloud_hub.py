"""
Backward-compatibility shim for cloud_hub module.
All logic has been moved to api.wa_hub.
"""

from .wa_hub import router

__all__ = ["router"]

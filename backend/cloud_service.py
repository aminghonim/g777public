"""
Backward-compatibility shim for cloud_service module.
All logic has been moved to backend.wa_gateway.
This file is kept to prevent import errors during the refactor transition.
"""

from .wa_gateway import (
    WAGateway,
    wa_gateway,
    cloud_service,
    AzureCloudService,
    G777CloudService,
)

__all__ = [
    "WAGateway",
    "wa_gateway",
    "cloud_service",
    "AzureCloudService",
    "G777CloudService",
]

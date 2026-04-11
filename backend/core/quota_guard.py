from fastapi import HTTPException, Depends, status
from typing import Dict, Any
from backend.database_manager import db_manager
from core.dependencies import get_current_user


class QuotaGuard:
    """
    SAAS-013: Security & Resource Enforcement Dependency.
    Checks tenant usage against Tier-based quotas.
    """

    GUEST_USER_ID = "00000000-0000-0000-0000-000000000000"

    @classmethod
    def _get_effective_user_id(cls, current_user: Dict[str, Any]) -> str:
        return (
            current_user.get("user_id") or current_user.get("sub") or cls.GUEST_USER_ID
        )

    @classmethod
    async def check_message_quota(
        cls, current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        """Verifies if the tenant has daily message budget remaining."""
        user_id = cls._get_effective_user_id(current_user)

        # High-performance check
        quota = db_manager.get_user_quota_info(user_id)
        if quota["message_count"] >= quota["daily_limit"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "QUOTA_EXCEEDED",
                    "code": 403,
                    "message": f"Daily limit of {quota['daily_limit']} messages reached.",
                    "upgrade_url": "/settings/billing",
                    "current": quota["message_count"],
                    "limit": quota["daily_limit"],
                },
            )
        return True

    @classmethod
    async def check_instance_quota(
        cls, current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        """Verifies if the tenant has available WhatsApp instance slots."""
        user_id = cls._get_effective_user_id(current_user)

        quota = db_manager.get_user_quota_info(user_id)
        if quota["instance_count"] >= quota["max_instances"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "INSTANCE_LIMIT_REACHED",
                    "code": 403,
                    "message": f"Tier limit of {quota['max_instances']} WhatsApp instances reached.",
                    "upgrade_url": "/settings/billing",
                    "current": quota["instance_count"],
                    "limit": quota["max_instances"],
                },
            )
        return True

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from backend.database_manager import db_manager
from core.dependencies import get_current_user
from backend.core.evolution_manager import (
    evolution_manager,
    EvolutionAPIError,
    EvolutionIsolationError,
)
from backend.core.quota_guard import QuotaGuard

router = APIRouter()


@router.post(
    "/create",
    response_model=Dict[str, Any],
    dependencies=[Depends(QuotaGuard.check_instance_quota)],
)
async def create_instance(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    SAAS-011: Dynamically create an isolated WhatsApp instance for the tenant.
    No parameters from the client are accepted.
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid user_id not found in token.",
        )

    try:
        response = await evolution_manager.create_instance(user_id=user_id)
        # SAAS-013: Atomic instance accounting
        db_manager.increment_daily_usage(user_id, "instance_count")
        return response
    except EvolutionIsolationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EvolutionAPIError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except Exception as e:
        # ASVS V16.5.1: Generic fallback error message without stack trace.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during instance provisioning.",
        )


@router.get(
    "/qr",
    response_model=Dict[str, Any],
    dependencies=[Depends(QuotaGuard.check_instance_quota)],
)
async def get_qr_code(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    SAAS-011: Fetch the QR code for the tenant's isolated instance.
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token state."
        )

    try:
        response = await evolution_manager.get_qr_code(user_id=user_id)
        return response
    except EvolutionIsolationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EvolutionAPIError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve QR code.",
        )


@router.get("/status", response_model=Dict[str, Any])
async def get_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    SAAS-011: Get connection status of the tenant's isolated instance.
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token state."
        )

    try:
        response = await evolution_manager.get_connection_state(user_id=user_id)
        return response
    except EvolutionIsolationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EvolutionAPIError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve instance status.",
        )


@router.delete("/delete", response_model=Dict[str, Any])
async def delete_instance(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    SAAS-011: Securely delete the tenant's isolated instance.
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token state."
        )

    try:
        success = await evolution_manager.delete_instance(user_id=user_id)
        # SAAS-013: Atomic instance decrement
        db_manager.decrement_instance_usage(user_id)
        return {"status": "success", "detail": "Instance successfully deleted."}
    except EvolutionIsolationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EvolutionAPIError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete instance.",
        )

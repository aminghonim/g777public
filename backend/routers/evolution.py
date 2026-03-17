from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging
import traceback
from pydantic import BaseModel
from backend.database_manager import db_manager
from core.dependencies import get_current_user, get_current_user_or_guest
from backend.core.evolution_manager import (
    evolution_manager,
    EvolutionAPIError,
    EvolutionIsolationError,
)
from backend.core.quota_guard import QuotaGuard

router = APIRouter()
logger = logging.getLogger(__name__)


class PairingCodeRequest(BaseModel):
    phone: str


@router.post(
    "/create",
    response_model=Dict[str, Any],
    dependencies=[Depends(QuotaGuard.check_instance_quota)],
)
async def create_instance(
    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),
):
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
        logger.error(f"Instance create error: {traceback.format_exc()}")
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
async def get_qr_code(current_user: Dict[str, Any] = Depends(get_current_user_or_guest)):
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
        # Flutter Proxy Pattern: Explicitly wrap in success/data to match PairingDialog.dart
        return {
            "success": True,
            "data": {
                "base64": response.get("qr_code_base64"),
                "status": response.get("status"),
                "instance": response.get("instance_name"),
            },
        }
    except EvolutionIsolationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EvolutionAPIError as e:
        # Return success=false to let UI handle the error state gracefully
        return {"success": False, "error": str(e)}
    except Exception:
        logger.error(f"QR Fetch Error: {traceback.format_exc()}")
        return {"success": False, "error": "Failed to retrieve QR code."}


@router.get(
    "/pairing-code",
    response_model=Dict[str, Any],
    dependencies=[Depends(QuotaGuard.check_instance_quota)],
)
async def get_pairing_code(
    phone: str,
    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),
):
    """
    SAAS-011: Request a pairing code from the local bridge (GET request for Flutter).
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token state."
        )

    try:
        response = await evolution_manager.get_pairing_code(user_id=user_id, phone=phone)
        return {
            "success": True,
            "code": response.get("code"),
            "instance": response.get("instance_name"),
        }
    except EvolutionIsolationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EvolutionAPIError as e:
        # Return 200 with success=false to show error in UI nicely
        return {"success": False, "message": str(e)}
    except Exception:
        logger.error(f"Pairing Code Fetch Error: {traceback.format_exc()}")
        return {"success": False, "message": "Failed to retrieve pairing code."}


@router.get("/status", response_model=Dict[str, Any])
async def get_status(current_user: Dict[str, Any] = Depends(get_current_user_or_guest)):
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
        return {"success": True, "data": response}
    except EvolutionIsolationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EvolutionAPIError as e:
        return {"success": False, "message": str(e)}
    except Exception:
        logger.error(f"Status Fetch Error: {traceback.format_exc()}")
        return {"success": False, "message": "Failed to retrieve instance status."}


@router.delete("/instance", response_model=Dict[str, Any])
async def delete_instance(
    current_user: Dict[str, Any] = Depends(get_current_user_or_guest),
):
    """
    SAAS-011: Remove the tenant's isolated WhatsApp instance.
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token state."
        )

    try:
        await evolution_manager.delete_instance(user_id=user_id)
        # SAAS-013: Atomic instance decrement or soft-delete logic here
        return {"success": True, "message": "Instance deleted successfully."}
    except EvolutionIsolationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EvolutionAPIError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except Exception:
        logger.error(f"Delete Instance Error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete instance.",
        )
@router.post("/logout", response_model=Dict[str, Any])
async def logout(current_user: Dict[str, Any] = Depends(get_current_user_or_guest)):
    """
    SAAS-011: Force logout and session reset.
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token state."
        )

    try:
        await evolution_manager.logout(user_id=user_id)
        return {"success": True, "message": "Logged out and session reset successfully."}
    except EvolutionIsolationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except EvolutionAPIError as e:
        return {"success": False, "message": str(e)}
    except Exception:
        logger.error(f"Logout Error: {traceback.format_exc()}")
        return {"success": False, "message": "Failed to logout."}

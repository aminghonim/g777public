import os
import secrets
import logging
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from core.security import SecurityEngine
from core.dependencies import get_current_user
from backend.database_manager import db_manager
from backend.core.security_sanitizer import SecuritySanitizer
from backend.services.cache_manager import cache_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# Guest endpoint rate limiting
GUEST_RATE_LIMIT_WINDOW = 60  # seconds
GUEST_RATE_LIMIT_MAX = 5  # max requests per window


def _check_guest_rate_limit(client_ip: str) -> bool:
    """
    Distributed sliding window rate limiter for guest token endpoint.
    Returns True if allowed, False if rate limited.
    """
    # Uses Upstash Redis via CacheManager to track requests per IP
    return cache_manager.check_rate_limit(
        identifier=f"guest_token:{client_ip}",
        limit=GUEST_RATE_LIMIT_MAX,
        window_seconds=GUEST_RATE_LIMIT_WINDOW,
    )


def _get_master_key() -> str:
    """
    Retrieve the master key from environment.
    If not set, returns None — master key functionality is disabled.
    In production, set DEV_MASTER_KEY to a cryptographically secure value
    generated at install time (e.g., secrets.token_urlsafe(32)).
    """
    return os.getenv("DEV_MASTER_KEY")


class LicenseActivationRequest(BaseModel):
    license_key: str
    hwid: str


class LicenseGenerationRequest(BaseModel):
    # This endpoint should be guarded by an Admin Dependency in prod!
    tier_id: int
    max_devices: int = 1
    days_valid: int = 30


@router.post("/activate")
async def activate_license(payload: LicenseActivationRequest):
    """
    SAAS-016: License Validation & HWID Binding.
    Validates the Key/HWID combination and returns a legacy-compliant JWT Token.
    """
    try:
        # SAAS-016.5: Resilient Master Key & Sanitization
        sanitized_key = (
            SecuritySanitizer.sanitize_input(payload.license_key)
            .replace(".", "")
            .replace("-", "")
            .upper()
        )
        sanitized_hwid = SecuritySanitizer.sanitize_input(payload.hwid)
        master_key = _get_master_key()
        if master_key:
            master_key = master_key.replace("-", "").replace(".", "").upper()
        else:
            master_key = None  # Master key disabled if not configured

        if master_key and sanitized_key == master_key:
            # God-Mode Token Generation (No DB Interaction)
            token_data = {
                "sub": "dev_master_007",
                "user_id": "dev_master_007",
                "username": "Dev-Admin",
                "role": "admin",
                "instance_name": "Inst_MasterKey",
                "tier": "enterprise",
            }
            token = SecurityEngine.create_access_token(token_data)
            return {
                "status": "success",
                "access_token": token,
                "token_type": "bearer",
                "message": "Developer Master Key Activated.",
            }

        # Regular Flow: Atomic Validation & Mapping
        user_data = db_manager.activate_or_validate_license(
            sanitized_key, sanitized_hwid
        )

        # Issue Standard JWT Token (100% untouched QuotaGuard / Tenant logic)
        token_data = {
            "sub": str(user_data["id"]),
            "user_id": str(user_data["id"]),
            "username": user_data["username"],
            "role": user_data["role"],
            "instance_name": user_data["instance_name"],
        }

        # Use existing SecurityEngine logic
        token = SecurityEngine.create_access_token(token_data)

        return {
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "message": "License Activated and Bound Successfully",
        }

    except Exception as e:
        # Prevent leaking verbose backend traces to client on failed HWID bounds
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/generate")
async def generate_license(
    payload: LicenseGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    SAAS-016: Generate secure license key using CSPRNG.
    Format: XXXXX-XXXXX-XXXXX-XXXXX
    Restricted to admin users only.
    """
    # Admin Guard: reject non-admin roles
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required to generate licenses.",
        )

    # 1. Use Cryptographically Secure Pseudo-Random Number Generator (CSPRNG ASVS Standard)
    raw_key = secrets.token_hex(10).upper()  # 20 Chars
    license_key = "-".join([raw_key[i : i + 5] for i in range(0, 20, 5)])

    # 2. Add to database
    conn = db_manager.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO licenses (license_key, tier_id, max_devices, expires_at) 
                VALUES (%s, %s, %s, NOW() + INTERVAL '%s days')
                """,
                (license_key, payload.tier_id, payload.max_devices, payload.days_valid),
            )
            conn.commit()
    finally:
        db_manager.release_connection(conn)

    return {
        "status": "success",
        "license_key": license_key,
        "tier_id": payload.tier_id,
        "max_devices": payload.max_devices,
        "days_valid": payload.days_valid,
    }


@router.post("/guest")
async def activate_guest(request: Request):
    """
    SAAS-017: Guest Session Token.
    Issues an isolated token for trial users.
    Rate limited to prevent token farming.
    """
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not _check_guest_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "RATE_LIMITED",
                "message": f"Too many guest token requests. Max {GUEST_RATE_LIMIT_MAX} per {GUEST_RATE_LIMIT_WINDOW}s.",
                "retry_after": GUEST_RATE_LIMIT_WINDOW,
            },
        )
    token_data = {
        "sub": "00000000-0000-0000-0000-000000000000",
        "user_id": "00000000-0000-0000-0000-000000000000",
        "username": "Trial Guest",
        "role": "guest",
        "instance_name": "Inst_Guest",
    }
    from core.security import SecurityEngine

    token = SecurityEngine.create_access_token(token_data)
    return {"status": "success", "access_token": token, "token_type": "bearer"}


@router.get("/status")
async def get_license_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    SAAS-019: License Status Endpoint.
    Returns the current license status including expiry date and days remaining.
    Accessible even when license is expired (exempt from LicenseGuard).
    """
    username = current_user.get("username", "")
    role = current_user.get("role", "")

    # Guest users have no license binding
    if role == "guest":
        return {
            "is_valid": True,
            "reason": "guest_access",
            "role": "guest",
            "expires_at": None,
            "days_remaining": None,
        }

    if db_manager is None or db_manager.pool is None:
        return {
            "is_valid": True,
            "reason": "no_database",
            "role": role,
            "expires_at": None,
            "days_remaining": None,
        }

    try:
        status_result = db_manager.check_license_status(username)
        status_result["role"] = role
        return status_result
    except Exception as e:
        logger.error(f"License status check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve license status",
        )

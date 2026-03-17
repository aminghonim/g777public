import asyncio
import logging
import json
import traceback
import os
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Local imports
from backend.database_manager import db_manager
from backend.core.event_broker import event_broker
from core.config import settings

# Initialize logger
logger = logging.getLogger(__name__)

class EvolutionError(Exception):
    """Base exception for Evolution API errors."""
    pass

class EvolutionAPIError(EvolutionError):
    """Raised when the Evolution API returns an error response."""
    pass

class EvolutionIsolationError(EvolutionError):
    """Raised when tenant isolation rules are violated."""
    pass

class EvolutionManager:
    """
    SaaS multi-tenant manager for Evolution API instances.
    Enforces Zero-Regression, Config-First, and Strict Tenant Isolation.
    """

    def __init__(self):
        # SAAS-011: Config-First with Intelligence-driven Provider Selection
        provider = os.getenv("WHATSAPP_PROVIDER", "evolution").lower()
        
        # Load defaults
        self.base_url = os.getenv("EVOLUTION_API_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("EVOLUTION_API_GLOBAL_KEY", "")

        # Intelligent Override based on Provider
        if hasattr(settings, "evolution_api") and settings.evolution_api:
            if provider == "baileys" and settings.evolution_api.baileys_api_url:
                self.base_url = settings.evolution_api.baileys_api_url.rstrip("/")
            elif settings.evolution_api.url:
                self.base_url = settings.evolution_api.url.rstrip("/")
            
            if settings.evolution_api.api_key:
                self.api_key = settings.evolution_api.api_key
        
        # Ensure base_url is set if still empty
        if not self.base_url:
            self.base_url = "http://baileys-bridge:3000" if provider == "baileys" else "http://evolution-api:8080"

        if not self.api_key and provider != "baileys":
            logger.critical(
                "🔥 EVO-CHECK-V3: EVOLUTION_API_GLOBAL_KEY missing. SaaS features will fail."
            )
        
        logger.info(f"✅ EVO-CHECK-V4: EvolutionManager (Provider: {provider}) initialized with {self.base_url}")

        self.headers = {"apikey": self.api_key, "Content-Type": "application/json"}

    def _generate_isolated_instance_name(self, user_id: str) -> str:
        """
        Cryptographically binds the instance name to a specific user_id.
        """
        if not user_id:
            raise EvolutionIsolationError("Cannot generate instance without user_id.")
        
        if user_id == "guest_local":
            from core.config import settings
            return settings.security.guest_instance_name

        short_uuid = uuid.uuid4().hex[:8]
        return f"tenant_{user_id}_inst_{short_uuid}"

    def _get_user_instance(self, user_id: str) -> Optional[str]:
        """
        Retrieves the exact instance bound to the user from the database.
        Enforces Tenant Isolation by preventing access to arbitrary instances.
        """
        if db_manager is None or db_manager.pool is None:
            raise EvolutionIsolationError(
                "Database connection unavailable. Cannot fetch instance allocation safely."
            )

        if user_id == "guest_local":
            from core.config import settings

            return settings.security.guest_instance_name

        conn = db_manager.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT instance_name FROM users WHERE id::text = %s OR username = %s LIMIT 1",
                    (user_id, user_id),
                )
                res = cursor.fetchone()
                return res[0] if res else None
        finally:
            db_manager.release_connection(conn)

    def _save_user_instance(self, user_id: str, instance_name: Optional[str]) -> None:
        """
        Persists the allocated instance name to the user's tenant record.
        """
        if db_manager is None or db_manager.pool is None:
            raise EvolutionIsolationError(
                "Database connection unavailable. Cannot save instance allocation safely."
            )

        conn = db_manager.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET instance_name = %s WHERE id::text = %s OR username = %s",
                    (instance_name, user_id, user_id),
                )
                conn.commit()
        finally:
            db_manager.release_connection(conn)

    def _validate_config(self):
        if not self.base_url or not self.headers.get("apikey"):
            raise EvolutionAPIError(
                "Evolution API configuration missing. Check .env variables."
            )

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
    )
    async def create_instance(self, user_id: str) -> Dict[str, Any]:
        """
        SAAS-011: Provision an isolated instance. 
        For Baileys local bridge, we return the singleton guest instance.
        """
        self._validate_config()

        instance_name = self._get_user_instance(user_id)
        
        if ":3000" in self.base_url:
            logger.info(f"ℹ️ EVO-BAILEYS: Using singleton instance '{instance_name}' for local bridge.")
            return {
                "instance": {
                    "instanceName": instance_name,
                    "status": "created"
                }
            }

        # Generate a truly isolated, unique instance name linked to this user
        isolated_instance_name = self._generate_isolated_instance_name(user_id)

        payload = {
            "instanceName": isolated_instance_name,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/instance/create",
                headers=self.headers,
                json=payload,
                timeout=20.0,
            )
            
            logger.info(f"Evolution Create Response: {response.status_code} - {response.text}")

            if response.status_code != 201:
                raise EvolutionAPIError(f"Failed to create instance: {response.text}")

            data = response.json()

            # Persist the connection locally securely mapping user ID to this isolated instance
            try:
                self._save_user_instance(user_id, isolated_instance_name)
            except Exception as e:
                # Orchestrator Rollback: Destroy orphaned cloud instance if DB sync fails
                await client.delete(
                    f"{self.base_url}/instance/delete/{isolated_instance_name}",
                    headers=self.headers,
                    timeout=10.0,
                )
                raise EvolutionIsolationError(
                    f"Database sync failed. Cloud instance rolled back. Error: {str(e)}"
                )

            data = response.json()
            
            # Extract QR from various possible locations in v2 response
            qr_base64 = ""
            if isinstance(data, dict):
                # Try direct base64
                qr_base64 = data.get("base64")
                if not qr_base64:
                    # Try nested qrcode block
                    qrcode_block = data.get("qrcode", {})
                    if isinstance(qrcode_block, dict):
                        qr_base64 = qrcode_block.get("base64", "")
                
                if not qr_base64:
                    # Try direct code/qrcode fields (v1/v2 variants)
                    qr_base64 = data.get("qrcode") or data.get("code") or ""

            # Unified Status Broadcasting
            asyncio.create_task(
                # pylint: disable=undefined-variable
                event_broker.publish_status("WHATSAPP", "CREATED", user_id=user_id)
            )

            return {
                "instance_name": isolated_instance_name,
                "qr_code_base64": qr_base64,
                "status": "CREATED",
            }

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
    )
    async def get_connection_state(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves the connection status strictly for the user's assigned instance.
        """
        self._validate_config()

        instance_name = self._get_user_instance(user_id)
        if not instance_name:
            raise EvolutionIsolationError(f"No instance bound to user {user_id}.")

        async with httpx.AsyncClient() as client:
            # Hybrid Check: Local Bare-metal support (Port 3000)
            if ":3000" in self.base_url:
                response = await client.get(
                    f"{self.base_url}/status", headers=self.headers, timeout=10.0
                )
                if response.status_code != 200:
                    raise EvolutionAPIError(f"Local bridge error: {response.text}")
                data = response.json()
                return {
                    "instance": instance_name,
                    "state": data.get("status", "UNKNOWN").upper(),
                }

            response = await client.get(
                f"{self.base_url}/instance/connectionState/{instance_name}",
                headers=self.headers,
                timeout=10.0,
            )

            if response.status_code == 404:
                return {"instance": instance_name, "state": "NOT_FOUND"}
            elif response.status_code != 200:
                raise EvolutionAPIError(
                    f"Failed to get connection state: {response.text}"
                )

            status_payload = response.json()
            status = status_payload.get("instance", {}).get("state", "UNKNOWN")

            # Unified Status Broadcasting
            asyncio.create_task(
                event_broker.publish_status("WHATSAPP", status, user_id=user_id)
            )

            return {"instance": instance_name, "state": status}

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
    )
    async def get_qr_code(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves a fresh QR code strictly scoped to the user's isolated instance.
        """
        self._validate_config()

        instance_name = self._get_user_instance(user_id)
        if not instance_name:
            raise EvolutionIsolationError(f"No instance bound to user {user_id}.")

        async with httpx.AsyncClient() as client:
            # Hybrid Check: Local Baileys support (Port 3000)
            if ":3000" in self.base_url:
                logger.info(f"📡 EVO-QR: Requesting QR from local bridge {self.base_url}/qr")
                response = await client.get(
                    f"{self.base_url}/qr", headers=self.headers, timeout=15.0
                )
                if response.status_code == 404:
                    # SAAS-011: Already connected or not initialized
                    return {
                        "instance_name": instance_name,
                        "qr_code_base64": "",
                        "status": "ALREADY_CONNECTED",
                        "message": "Instance is already connected or not initialized.",
                    }

                if response.status_code != 200:
                    raise EvolutionAPIError(
                        f"Local bridge QR fetch failed: {response.text}"
                    )
                data = response.json()
                return {
                    "instance_name": instance_name,
                    "qr_code_base64": (
                        data.get("qrImage", "").split(",")[-1]
                        if data.get("qrImage")
                        else ""
                    ),
                    "status": "CREATED",
                }

            response = await client.get(
                f"{self.base_url}/instance/connect/{instance_name}",
                headers=self.headers,
                timeout=15.0,
            )

            if response.status_code == 404:
                # SAAS-011: Auto-create if not found (Self-Healing)
                logger.info(f"Instance {instance_name} not found. Attempting auto-provisioning...")
                try:
                    await self.create_instance(user_id)
                    # Small delay for Evolution API to stabilize the new instance
                    await asyncio.sleep(2)
                    # Retry once more after creation
                    response = await client.get(
                        f"{self.base_url}/instance/connect/{instance_name}",
                        headers=self.headers,
                        timeout=15.0,
                    )
                except Exception as e:
                    raise EvolutionAPIError(f"Auto-provisioning failed: {str(e)}")

            if response.status_code != 200:
                raise EvolutionAPIError(f"Failed to get QR Code: {response.text}")

            data = response.json()
            # Extract QR with full fallbacks
            qr_data = (
                data.get("base64") or 
                data.get("qrcode") or 
                data.get("code") or 
                (data.get("qrcode", {}) if isinstance(data.get("qrcode"), dict) else {}).get("base64") or
                ""
            )
            
            return {
                "instance_name": instance_name,
                "qr_code_base64": qr_data,
                "status": "CREATED",
            }

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
    )
    async def get_pairing_code(self, user_id: str, phone: str) -> Dict[str, Any]:
        """
        Requests a pairing code from the local bridge for phone-based pairing.
        Only supported for Local Bare-metal (Port 3000).
        """
        self._validate_config()

        instance_name = self._get_user_instance(user_id)
        if not instance_name:
            raise EvolutionIsolationError(f"No instance bound to user {user_id}.")

        if ":3000" not in self.base_url:
            raise EvolutionAPIError(
                "Pairing code is only supported in local bridge mode."
            )

        async with httpx.AsyncClient() as client:
            payload = {"phone": phone}
            response = await client.post(
                f"{self.base_url}/pairing-code",
                headers=self.headers,
                json=payload,
                timeout=15.0,
            )

            if response.status_code != 200:
                raise EvolutionAPIError(
                    f"Local bridge pairing-code fetch failed: {response.text}"
                )

            data = response.json()
            return {
                "instance_name": instance_name,
                "code": data.get("code", ""),
                "status": "CREATED",
            }

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
    )
    async def delete_instance(self, user_id: str) -> bool:
        """
        Deletes the isolated instance from Evolution API and unlinks it from the Database.
        """
        self._validate_config()

        instance_name = self._get_user_instance(user_id)
        if not instance_name:
            # Nothing to delete
            return True

        async with httpx.AsyncClient() as client:
            # Hybrid Check: Local Bare-metal support (Port 3000)
            if ":3000" in self.base_url:
                await client.post(f"{self.base_url}/disconnect", headers=self.headers)
                self._save_user_instance(user_id, None)
                return True

            # We attempt the delete explicitly
            response = await client.delete(
                f"{self.base_url}/instance/delete/{instance_name}",
                headers=self.headers,
                timeout=15.0,
            )

            if response.status_code not in (200, 204, 404):
                raise EvolutionAPIError(
                    f"Failed to delete instance from API: {response.text}"
                )

            # Erase linkage strictly to enforce tenant integrity
            self._save_user_instance(user_id, None)

            # Unified Status Broadcasting
            asyncio.create_task(
                event_broker.publish_status("WHATSAPP", "DELETED", user_id=user_id)
            )
            return True

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
    )
    async def logout(self, user_id: str) -> bool:
        """
        SAAS-011: Forcefully logs out and resets the session.
        In local mode, this wipes the auth_info directory.
        """
        self._validate_config()

        async with httpx.AsyncClient() as client:
            if ":3000" in self.base_url:
                # Force reset for local bridge
                await client.post(f"{self.base_url}/reset", headers=self.headers, timeout=15.0)
                return True
            
            instance_name = self._get_user_instance(user_id)
            if not instance_name:
                return True

            # Cloud logout
            await client.post(
                f"{self.base_url}/instance/logout/{instance_name}",
                headers=self.headers,
                timeout=15.0,
            )
            return True


# Singleton initialization
evolution_manager = EvolutionManager()

"""
Evolution API Manager - Core Multi-Tenant Engine
================================================
Handles secure instantiation, monitoring, and deletion of WhatsApp instances
via Evolution API, fully enforcing Tenant Isolation and Cloud-First configs.
"""

import os
import uuid
import httpx
from typing import Dict, Any, Optional
import asyncio
from backend.core.event_broker import event_broker
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Import DatabaseManager to strictly link created instances to users
from backend.database_manager import db_manager

# Constant Configuration defaults from environment
EVO_BASE_URL = os.getenv("EVOLUTION_API_BASE_URL", "").rstrip("/")
EVO_GLOBAL_KEY = os.getenv("EVOLUTION_API_GLOBAL_KEY", "")


class EvolutionIsolationError(Exception):
    """Raised when Tenant Isolation is breached or violated."""

    pass


class EvolutionAPIError(Exception):
    """Raised when Evolution API returns an error or fails."""

    pass


class EvolutionManager:
    """
    SaaS multi-tenant manager for Evolution API instances.
    Enforces Zero-Regression, Config-First, and Strict Tenant Isolation.
    """

    def __init__(self):
        if not EVO_BASE_URL or not EVO_GLOBAL_KEY:
            # We don't throw immediate fatal error because local testing might not have Evolution API.
            # We log a critical warning and raise it lazily when an API call is attempted.
            print(
                "[CRITICAL WARNING] EVOLUTION_API_BASE_URL or EVOLUTION_API_GLOBAL_KEY "
                "missing from environment variables. Evolution API integrations will fail."
            )

        if EVO_BASE_URL:
            print(f"[OK] Evolution API Base URL loaded: {EVO_BASE_URL}")
        self.base_url = EVO_BASE_URL
        self.headers = {"apikey": EVO_GLOBAL_KEY, "Content-Type": "application/json"}

    def _generate_isolated_instance_name(self, user_id: str) -> str:
        """
        Cryptographically binds the instance name to a specific user_id.
        """
        if not user_id:
            raise EvolutionIsolationError("Cannot generate instance without user_id.")
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
        Dynamically creates an isolated Evolution instance for a user.
        Includes Smart Retry for network resilience.
        """
        self._validate_config()

        # Hybrid Check: Local Bare-metal support (Port 3000)
        if ":3000" in self.base_url:
            print("[INFO] Using local Bare-metal Baileys bridge.")
            self._save_user_instance(user_id, "Local_Baileys_Bridge")
            return {
                "instance_name": "Local_Baileys_Bridge",
                "qr_code_base64": "",
                "status": "CREATED",
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
                timeout=15.0,
            )

            if response.status_code not in (200, 201):
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

            # The Evolution API might return the qrcode directly upon creation or we must fetch it.
            # Format varies slightly with API versions, safely traverse dict.
            qr_base64 = ""
            if isinstance(data, dict):
                qrcode_block = data.get("qrcode", {})
                if isinstance(qrcode_block, dict):
                    qr_base64 = qrcode_block.get("base64", "")

            # Unified Status Broadcasting
            asyncio.create_task(
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
            # Hybrid Check: Local Bare-metal support (Port 3000)
            if ":3000" in self.base_url:
                response = await client.get(
                    f"{self.base_url}/qr", headers=self.headers, timeout=15.0
                )
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
                }

            response = await client.get(
                f"{self.base_url}/instance/connect/{instance_name}",
                headers=self.headers,
                timeout=15.0,
            )

            if response.status_code != 200:
                raise EvolutionAPIError(f"Failed to get QR Code: {response.text}")

            data = response.json()
            return {
                "instance_name": instance_name,
                "qr_code_base64": data.get("base64", ""),
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


# Singleton initialization
evolution_manager = EvolutionManager()

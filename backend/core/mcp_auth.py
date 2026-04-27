"""
MCP Authentication Layer
Checks for X-MCP-Token/API-Keys before allowing tool discovery or invocation.
Implements timing-attack protection and audit logging.
"""

import os
import hmac
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class MCPAuthenticator:
    """
    Singleton authenticator for MCP tools.
    Validates keys against MCP_API_KEYS environment variable.
    Format: key1:perm1,key2:perm2
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPAuthenticator, cls).__new__(cls)
            cls._instance._keys = {}
            cls._instance._load_keys()
        return cls._instance

    def _load_keys(self):
        """Loads and parses keys from environment."""
        raw_keys = os.getenv("MCP_API_KEYS", "")
        self._keys = {}
        if not raw_keys:
            logger.warning("MCP_API_KEYS not set. MCP tools are DISABLED.")
            return

        for entry in raw_keys.split(","):
            if ":" in entry:
                key, perm = entry.split(":", 1)
                self._keys[key.strip()] = perm.strip()
            else:
                # Default to 'full' if no permission specified
                self._keys[entry.strip()] = "full"

    def validate(self, api_key: Optional[str], required_perm: str = "full") -> bool:
        """
        Validates the provided API key against allowed permissions.
        Uses hmac.compare_digest to prevent timing attacks.
        """
        # Reload keys if env changed (useful for tests and dynamic updates)
        self._load_keys()

        if not api_key or not self._keys:
            return False

        # Iterate securely to find the key
        for stored_key, stored_perm in self._keys.items():
            if hmac.compare_digest(stored_key, api_key):
                # Permission check
                if stored_perm == "full":
                    return True  # Full grants everything
                return stored_perm == required_perm

        return False

    def audit_log(self, caller: str, tool: str, success: bool):
        """Logs access attempts for security auditing."""
        status = "ALLOWED" if success else "DENIED"
        level = logging.INFO if success else logging.WARNING
        logger.log(level, f"MCP Access {status} | Caller: {caller} | Tool: {tool}")


from fastapi import Header, HTTPException, status

async def get_mcp_token(x_mcp_token: Optional[str] = Header(None)) -> str:
    """
    FastAPI dependency to extract X-MCP-Token from headers.
    """
    if not x_mcp_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-MCP-Token header",
        )
    return x_mcp_token

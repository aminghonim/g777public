"""
Security Tests — M8: MCP Tools No Authentication (TDD RED → GREEN)
Tests that verify MCP tools require a valid API key before invocation.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================================
# M8: MCP Tool Authentication Layer
# ============================================================================

class TestMCPAuthenticator:
    """Tests for the MCPAuthenticator class."""

    def setup_method(self):
        """Clear any cached authenticator state before each test."""
        from backend.core.mcp_auth import MCPAuthenticator
        # Reset singleton
        MCPAuthenticator._instance = None

    def teardown_method(self):
        """Clean up env vars after each test."""
        os.environ.pop("MCP_API_KEYS", None)
        # Reset singleton so next test starts fresh
        from backend.core.mcp_auth import MCPAuthenticator
        MCPAuthenticator._instance = None

    # --- Test 1: No key → MCP disabled ---
    def test_no_key_disabled_mcp(self):
        """
        M8: When MCP_API_KEYS env var is not set, validate() returns False.
        MCP tools must be disabled by default.
        """
        os.environ.pop("MCP_API_KEYS", None)
        from backend.core.mcp_auth import MCPAuthenticator
        auth = MCPAuthenticator()
        assert auth.validate(None) is False
        assert auth.validate("anything") is False

    # --- Test 2: Valid key with full access ---
    def test_valid_key_full_access(self):
        """
        M8: A valid key with 'full' permission grants access to call_tool().
        """
        os.environ["MCP_API_KEYS"] = "test-key-full:full"
        from backend.core.mcp_auth import MCPAuthenticator
        auth = MCPAuthenticator()
        assert auth.validate("test-key-full", required_perm="full") is True

    # --- Test 3: Read-only key cannot call tools ---
    def test_valid_key_read_only(self):
        """
        M8: A key with only 'read' permission can discover tools
        but cannot invoke them.
        """
        os.environ["MCP_API_KEYS"] = "test-key-read:read"
        from backend.core.mcp_auth import MCPAuthenticator
        auth = MCPAuthenticator()
        # Can read (discover tools)
        assert auth.validate("test-key-read", required_perm="read") is True
        # Cannot call tools
        assert auth.validate("test-key-read", required_perm="full") is False

    # --- Test 4: Invalid key rejected ---
    def test_invalid_key_rejected(self):
        """
        M8: A wrong API key is rejected.
        """
        os.environ["MCP_API_KEYS"] = "correct-key:full"
        from backend.core.mcp_auth import MCPAuthenticator
        auth = MCPAuthenticator()
        assert auth.validate("wrong-key") is False

    # --- Test 5: Timing attack protection ---
    def test_timing_attack_protection(self):
        """
        M8: Key comparison uses hmac.compare_digest() to prevent
        timing-based side-channel attacks.
        """
        import inspect
        from backend.core.mcp_auth import MCPAuthenticator
        source = inspect.getsource(MCPAuthenticator.validate)
        assert "hmac.compare_digest" in source, (
            "MCPAuthenticator.validate must use hmac.compare_digest() "
            "to prevent timing attacks"
        )

    # --- Test 6: Audit log on denial ---
    def test_audit_log_on_deny(self, caplog):
        """
        M8: When a call is denied, an audit log entry is created.
        """
        import logging
        os.environ["MCP_API_KEYS"] = "real-key:full"
        from backend.core.mcp_auth import MCPAuthenticator
        auth = MCPAuthenticator()
        with caplog.at_level(logging.INFO, logger="backend.core.mcp_auth"):
            auth.audit_log(caller="attacker", tool="filesystem__read", success=False)
        assert "DENIED" in caplog.text
        assert "attacker" in caplog.text
        assert "filesystem__read" in caplog.text


class TestMCPManagerAuthIntegration:
    """Tests that MCPManager enforces authentication."""

    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Set up valid API keys for tests."""
        os.environ["MCP_API_KEYS"] = "test-full-key:full,test-read-key:read"
        # Reset authenticator singleton
        from backend.core.mcp_auth import MCPAuthenticator
        MCPAuthenticator._instance = None
        yield
        os.environ.pop("MCP_API_KEYS", None)
        MCPAuthenticator._instance = None

    # --- Test 7: call_tool without key fails ---
    @pytest.mark.anyio
    async def test_mcp_manager_call_without_key_fails(self):
        """
        M8: mcp_manager.call_tool() without api_key returns an error.
        """
        from backend.mcp_manager import mcp_manager

        # Mock stdio_client to ensure it's NOT called
        with patch("backend.mcp_manager.stdio_client") as mock_stdio:
            result = await mcp_manager.call_tool("test__tool", {"arg": "val"})
            assert "Authentication failed" in result or "Error" in result
            # stdio_client must NOT be called
            mock_stdio.assert_not_called()

    # --- Test 8: call_tool with valid key proceeds ---
    @pytest.mark.anyio
    async def test_mcp_manager_call_with_valid_key_succeeds(self):
        """
        M8: mcp_manager.call_tool() with a valid api_key proceeds to invocation.
        """
        from backend.mcp_manager import mcp_manager
        from mcp import StdioServerParameters
        mcp_manager.server_params["test"] = StdioServerParameters(command="test", args=[], env={})

        # Mock stdio_client session
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.content = [MagicMock(text="tool output")]
        mock_session.call_tool = AsyncMock(return_value=mock_result)
        mock_session.initialize = AsyncMock()

        mock_read = AsyncMock()
        mock_write = AsyncMock()

        with patch("backend.mcp_manager.stdio_client") as mock_stdio:
            mock_stdio.return_value.__aenter__ = AsyncMock(return_value=(mock_read, mock_write))
            mock_stdio.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("backend.mcp_manager.ClientSession") as mock_session_cls:
                mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

                result = await mcp_manager.call_tool(
                    "test__tool",
                    {"arg": "val"},
                    api_key="test-full-key",
                    caller="test"
                )

                # Session.call_tool must have been invoked
                mock_session.call_tool.assert_called_once()
                assert "Authentication failed" not in result

    # --- Test 9: Multi-key isolation ---
    def test_multi_key_isolation(self):
        """
        M8: A read-only key cannot be used to gain full access.
        Keys are isolated from each other.
        """
        from backend.core.mcp_auth import MCPAuthenticator
        auth = MCPAuthenticator()
        # Full key works for full
        assert auth.validate("test-full-key", required_perm="full") is True
        # Read key works for read
        assert auth.validate("test-read-key", required_perm="read") is True
        # Read key does NOT work for full
        assert auth.validate("test-read-key", required_perm="full") is False
        # Full key does NOT work as read (it's 'full', not 'read')
        # Actually 'full' should grant all permissions — let's verify
        assert auth.validate("test-full-key", required_perm="read") is True

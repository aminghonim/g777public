"""
Integration Tests: RTK Enforcement Guard

Proves that:
1. Direct subprocess calls in agent tools are blocked
2. SystemCommandExecutor calls are allowed
3. Violations are logged with helpful messages
4. Bypass works for legitimate testing
"""

import pytest
import subprocess
import asyncio
from unittest.mock import patch, MagicMock


class TestEnforcementBlocking:
    """Test that enforcement blocks direct subprocess calls."""
    
    def test_subprocess_run_blocked_from_tools(self):
        """
        Verify that subprocess.run() raises RuntimeError when called
        from a restricted module like backend.tools.
        """
        from backend.core.rtk_enforcement import _check_enforcement
        
        # Pass the module explicitly to avoid dangerous sys._getframe patching
        with pytest.raises(RuntimeError) as exc_info:
            _check_enforcement("run", caller_module="backend.tools.bash_tool")
        
        assert "SystemCommandExecutor" in str(exc_info.value)
    
    def test_subprocess_popen_blocked_from_mcp(self):
        """Verify Popen is blocked from MCP server modules."""
        from backend.core.rtk_enforcement import _check_enforcement
        
        with pytest.raises(RuntimeError):
            _check_enforcement("Popen", caller_module="backend.mcp_server.git_tools")


class TestEnforcementWhitelist:
    """Test that whitelisted modules can use subprocess."""
    
    def test_browser_core_allowed(self):
        """Verify browser_core is whitelisted."""
        from backend.core.rtk_enforcement import _check_enforcement
        
        # Should NOT raise
        _check_enforcement("run", caller_module="backend.browser_core")
    
    def test_system_router_allowed(self):
        """Verify system router is whitelisted."""
        from backend.core.rtk_enforcement import _check_enforcement
        
        # Should NOT raise
        _check_enforcement("run", caller_module="backend.routers.system")


class TestSystemCommandExecutor:
    """Test that SystemCommandExecutor is the approved way."""
    
    def test_executor_works(self, executor_fixture):
        """Verify SystemCommandExecutor executes successfully."""
        async def run_test():
            result = await executor_fixture.execute("echo 'Hello Enforcement'")
            assert result["status"] == "success"
            assert "Hello Enforcement" in result["output"]
        
        asyncio.run(run_test())
    
    def test_executor_has_audit_trail(self, executor_fixture):
        """Verify executor produces audit trail."""
        async def run_test():
            result = await executor_fixture.execute("echo test")
            assert "metadata" in result
            assert "audit_trail" in result["metadata"]
            assert "compression_ratio" in result["metadata"]
            
        asyncio.run(run_test())


class TestEnforcementBypass:
    """Test that TemporaryEnforcementBypass works for testing."""
    
    def test_bypass_fixture(self, allow_subprocess):
        """
        Verify that allow_subprocess fixture enables direct subprocess.
        """
        # This will actually run a real command
        result = subprocess.run(
            "echo 'Bypass test'",
            shell=True,
            capture_output=True,
            text=True,
        )
        assert "Bypass test" in result.stdout


class TestEnforcementLogging:
    """Test that enforcement violations are properly logged."""
    
    def test_violation_logs_helpful_message(self, caplog):
        """Verify violation error message is helpful."""
        from backend.core.rtk_enforcement import _check_enforcement
        
        with caplog.at_level("ERROR"):
            try:
                _check_enforcement("run", caller_module="backend.tools.bash_tool")
            except RuntimeError as e:
                assert "SystemCommandExecutor" in str(e)
                assert "backend.tools.bash_tool" in str(e)
    
    def test_violation_includes_stack_trace(self, caplog):
        """Verify violation includes stack trace in logs."""
        from backend.core.rtk_enforcement import _check_enforcement
        
        with caplog.at_level("ERROR"):
            try:
                _check_enforcement("run", caller_module="backend.tools.bash_tool")
            except RuntimeError:
                pass
            
            assert "Stack trace" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

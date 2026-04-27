import pytest
import asyncio
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from core.lifespan import lifespan, supabase_keep_alive

def test_lifespan_creates_keep_alive_task():
    """Test that lifespan properly creates and cancels the heartbeat task."""
    app = FastAPI()
    
    async def run_test():
        with patch("core.security.SecurityEngine.create_session_lock") as mock_lock, \
             patch("backend.startup_checks.validate_webhook_reachability") as mock_checks, \
             patch("core.security.SecurityEngine.cleanup_session") as mock_cleanup, \
             patch("asyncio.create_task") as mock_create_task:
            
            # Create a mock task to return from create_task
            mock_task = MagicMock()
            mock_create_task.return_value = mock_task
            
            async with lifespan(app):
                # Assertions inside context
                mock_lock.assert_called_once()
                mock_checks.assert_called_once()
                
                # Verify the task was created
                mock_create_task.assert_called_once()
                args, _ = mock_create_task.call_args
                assert args[0].__name__ == supabase_keep_alive.__name__
            
            # After context yields
            mock_task.cancel.assert_called_once()
            mock_cleanup.assert_called_once()

    asyncio.run(run_test())

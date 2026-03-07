
import pytest
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.controllers.account_warmer_controller import AccountWarmerController

class TestAccountWarmerControllerSurgical:
    """
    Surgical tests for AccountWarmerController
    """

    @pytest.fixture
    def controller(self):
        with patch('ui.controllers.account_warmer_controller.cloud_service', MagicMock()):
            with patch('ui.controllers.account_warmer_controller.AccountWarmer', MagicMock()) as MockWarmer:
                ctrl = AccountWarmerController()
                return ctrl

    @pytest.mark.asyncio
    async def test_start_warming_success(self, controller):
        controller.warmer.generate_human_like_message = AsyncMock(return_value="Hello AI")
        
        with patch('ui.controllers.account_warmer_controller.cloud_service.send_whatsapp_message') as mock_send:
            mock_send.return_value = (True, "OK")
            
            log_callback = MagicMock()
            # Run for 2 messages with 0 delay for speed
            await controller.start_warming(
                phone1="123", 
                phone2="456", 
                count=2, 
                delay=0, 
                log_callback=log_callback
            )
            
            assert controller.state['is_running'] is False
            assert controller.state['current_count'] == 2
            assert mock_send.call_count == 2
            # Verify targets alternated
            mock_send.assert_any_call("123", "Hello AI")
            mock_send.assert_any_call("456", "Hello AI")
            assert "completed" in controller.get_logs()

    @pytest.mark.asyncio
    async def test_start_warming_stop_manual(self, controller):
        controller.warmer.generate_human_like_message = AsyncMock(return_value="Msg")
        
        # Callback that stops after first message
        def stop_after_one(msg):
            if "[1/5]" in msg: controller.stop_warming()

        with patch('ui.controllers.account_warmer_controller.cloud_service.send_whatsapp_message', return_value=(True, "OK")):
            await controller.start_warming(
                phone1="123", phone2="456", count=5, delay=0, 
                log_callback=stop_after_one
            )
            # Should stop after first message logic completes. 
            # Controller checks loop condition at start of loop.
            # If stopped during msg 1 callback (which happens after count update), next iteration (2) won't run.
            assert controller.state['current_count'] == 1
            assert "Stop requested" in controller.get_logs()

    @pytest.mark.asyncio
    async def test_start_warming_exception(self, controller):
        controller.warmer.generate_human_like_message.side_effect = Exception("AI Fail")
        
        await controller.start_warming("1", "2", 1, 0)
        assert "Error in warming: AI Fail" in controller.get_logs()
        assert controller.state['is_running'] is False

    def test_get_logs(self, controller):
        controller.state['logs'] = ["Log 1", "Log 2"]
        assert controller.get_logs() == "Log 1\nLog 2"

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Ensure backend/ui path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock nicegui/backend BEFORE import
sys.modules["nicegui"] = MagicMock()
sys.modules["backend.warmer"] = MagicMock()
sys.modules["backend.cloud_service"] = MagicMock()

from ui.modules.account_warmer import warmer_page

class TestAccountWarmerSurgical:
    """
    Surgical tests for ui/modules/account_warmer.py
    """
    
    @patch("ui.modules.account_warmer.theme_manager")
    @patch("ui.modules.account_warmer.ui")
    @patch("asyncio.sleep", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_warmer_logic(self, mock_sleep, mock_ui, mock_theme):
        """Test the start_warming logic flow by capturing the button callback."""
        # Get the global mocks
        mock_warmer_module = sys.modules["backend.warmer"]
        mock_cloud_module = sys.modules["backend.cloud_service"]
        
        mock_warmer_cls = mock_warmer_module.AccountWarmer
        mock_cloud = mock_cloud_module.cloud_service
        
        # Setup mocks
        mock_theme.get_colors.return_value = {"red": "#F00", "green": "#0F0"}
        mock_theme.get_semantic.return_value = {"negative": "#F00"}
        
        mock_warmer_instance = mock_warmer_cls.return_value
        mock_warmer_instance.is_running = False
        mock_warmer_instance.generate_human_like_message = AsyncMock(return_value="Hello World")
        
        # Capture UI elements to access values
        mock_phone1 = MagicMock()
        mock_phone1.value = "12345"
        mock_phone2 = MagicMock()
        mock_phone2.value = ""
        
        mock_msg_slider = MagicMock()
        mock_msg_slider.value = 1
        
        mock_delay_slider = MagicMock()
        mock_delay_slider.value = 0 # No delay
        
        mock_log_area = MagicMock()
        mock_start_btn = MagicMock()
        
        # Mock UI construction to return our controlled mocks
        # We need to wire up the returns so that when warmer_page calls ui.input(), we get our mocks
        # This is tricky because calls are sequential.
        # We can use side_effect on ui.input to return p1, p2
        mock_ui.input.side_effect = [mock_phone1, mock_phone2]
        mock_ui.slider.side_effect = [mock_msg_slider, mock_delay_slider]
        mock_ui.textarea.return_value = mock_log_area
        mock_ui.button.return_value = mock_start_btn
        
        # Run page setup
        warmer_page(None)
        
        # Extract the start_warming callback from the button call
        # ui.button(..., on_click=start_warming)
        args, kwargs = mock_ui.button.call_args
        start_warming_cb = kwargs.get('on_click')
        assert start_warming_cb is not None
        
        # --- TEST 1: Start Warming ---
        mock_cloud._send_evolution_text.return_value = (True, "OK")
        
        await start_warming_cb()
        
        # Verification
        assert mock_warmer_instance.is_running is False # Should be false at end of loop
        mock_warmer_instance.generate_human_like_message.assert_called_once()
        mock_cloud._send_evolution_text.assert_called_with("12345", "Hello World")
        assert mock_log_area.set_value.call_count >= 1
        
        # --- TEST 2: Stop Warming (Toggle) ---
        # Set running = True manually to simulate mid-run check if we call it again?
        # The function checks `if warmer.is_running:` at start.
        mock_warmer_instance.is_running = True
        await start_warming_cb()
        # Should set to False and return
        assert mock_warmer_instance.is_running is False

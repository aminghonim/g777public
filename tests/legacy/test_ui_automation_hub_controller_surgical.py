
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.controllers.automation_hub_controller import AutomationHubController

class TestAutomationHubControllerSurgical:
    """
    Surgical tests for AutomationHubController
    """

    @pytest.fixture
    def controller(self):
        with patch('ui.controllers.automation_hub_controller.cloud_service', MagicMock()):
            ctrl = AutomationHubController()
            return ctrl

    def test_get_instance_info(self, controller):
        with patch('ui.controllers.automation_hub_controller.cloud_service') as mock_service:
            mock_service.is_connected = True
            mock_service.instance_name = "TEST_INSTANCE"
            
            info = controller.get_instance_info()
            assert info['is_connected'] is True
            assert info['name'] == "TEST_INSTANCE"
            assert info['status'] == "Connected"

    def test_get_stats(self, controller):
        stats = controller.get_stats()
        assert 'active_campaigns' in stats
        assert stats['ai_model'] == "Gemini 2.0 Flash"

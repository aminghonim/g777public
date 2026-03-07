import pytest
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui.controllers.wa_hub_controller import WAHubController as CloudHubController


class TestCloudHubControllerSurgical:
    """
    Surgical tests for CloudHubController
    """

    @pytest.fixture
    def controller(self):
        with patch("ui.controllers.cloud_hub_controller.cloud_service", MagicMock()):
            ctrl = CloudHubController()
            return ctrl

    def test_check_connection(self, controller):
        with patch(
            "ui.controllers.cloud_hub_controller.cloud_service._verify_connection",
            return_value=True,
        ):
            assert controller.check_connection() is True
            assert controller.state["is_connected"] is True

    @pytest.mark.asyncio
    async def test_refresh_connection(self, controller):
        with patch(
            "ui.controllers.cloud_hub_controller.cloud_service._verify_connection",
            return_value=False,
        ):
            success = await controller.refresh_connection()
            assert success is False
            assert controller.state["is_connected"] is False

    @pytest.mark.asyncio
    async def test_ask_ai(self, controller):
        with patch(
            "ui.controllers.cloud_hub_controller.cloud_service.ask_ai_cloud",
            return_value="AI Response",
        ):
            response = await controller.ask_ai("Hello")
            assert response == "AI Response"
            assert len(controller.state["chat_history"]) == 2
            assert controller.state["chat_history"][0]["content"] == "Hello"

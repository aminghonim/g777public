
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.controllers.poll_sender_controller import PollSenderController

class TestPollSenderControllerSurgical:
    """
    Surgical tests for PollSenderController
    """

    @pytest.fixture
    def controller(self):
        with patch('ui.controllers.poll_sender_controller.DataGrabber', MagicMock()):
            ctrl = PollSenderController()
            return ctrl

    @pytest.mark.asyncio
    async def test_send_poll_success(self, controller):
        await controller.send_poll("Q?", ["A", "B"])
        controller.grabber.create_poll.assert_called_once_with("Q?", ["A", "B"])
        assert controller.state['is_sending'] is False

    @pytest.mark.asyncio
    async def test_send_poll_guard(self, controller):
        controller.state['is_sending'] = True
        await controller.send_poll("Q", ["A"])
        assert controller.grabber.create_poll.call_count == 0

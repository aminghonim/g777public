
import pytest
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.controllers.links_grabber_controller import LinksGrabberController

class TestLinksGrabberControllerSurgical:
    """
    Surgical tests for LinksGrabberController
    """

    @pytest.fixture
    def controller(self):
        with patch('ui.controllers.links_grabber_controller.GroupFinder', MagicMock()):
            ctrl = LinksGrabberController()
            return ctrl

    @pytest.mark.asyncio
    async def test_run_hunt_success(self, controller):
        controller.finder.find_groups = MagicMock(return_value=["https://chat.whatsapp.com/123"])
        
        # We need to mock the loop.run_in_executor to avoid actual threading overhead if possible
        # or just let it run if the mock is fast.
        
        links = await controller.run_hunt("real estate", 10)
        
        assert len(links) == 1
        assert "123" in links[0]['link']
        assert controller.state['is_hunting'] is False

    @pytest.mark.asyncio
    async def test_run_hunt_guard(self, controller):
        controller.state['is_hunting'] = True
        links = await controller.run_hunt("kw", 1)
        assert links == []

    def test_clear_results(self, controller):
        controller.state['results'] = [{"link": "..."}]
        controller.clear_results()
        assert controller.state['results'] == []

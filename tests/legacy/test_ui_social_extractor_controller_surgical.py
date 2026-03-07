
import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.controllers.social_extractor_controller import SocialExtractorController

class TestSocialExtractorControllerSurgical:
    """
    Surgical tests for SocialExtractorController
    """

    @pytest.fixture
    def controller(self):
        return SocialExtractorController()

    @pytest.mark.asyncio
    async def test_run_extraction_success(self, controller):
        results = await controller.run_extraction("LinkedIn", "http://test")
        assert len(results) == 1
        assert results[0]['platform'] == "LinkedIn"
        assert controller.state['is_extracting'] is False

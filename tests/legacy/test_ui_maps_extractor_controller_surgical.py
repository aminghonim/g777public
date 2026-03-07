
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.controllers.maps_extractor_controller import MapsExtractorController

class TestMapsExtractorControllerSurgical:
    """
    Surgical tests for MapsExtractorController
    """

    @pytest.fixture
    def controller(self):
        with patch('ui.controllers.maps_extractor_controller.MapsExtractor', MagicMock()):
            ctrl = MapsExtractorController()
            return ctrl

    @pytest.mark.asyncio
    async def test_run_extraction_success(self, controller):
        mock_results = [{'business': 'Shop A', 'phone': '123'}]
        controller.extractor.search_businesses = MagicMock(return_value=mock_results)
        
        results = await controller.run_extraction("coffee", "cairo", 10)
        assert results == mock_results
        assert controller.state['is_extracting'] is False

    @pytest.mark.asyncio
    async def test_run_extraction_guard(self, controller):
        controller.state['is_extracting'] = True
        results = await controller.run_extraction("q", "l", 1)
        assert results == []

    def test_get_suggestions(self, controller):
        controller.extractor.get_smart_suggestions = MagicMock(return_value=["gyms"])
        assert controller.get_suggestions() == ["gyms"]

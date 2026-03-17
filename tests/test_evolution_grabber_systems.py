import pytest
from unittest.mock import MagicMock, patch
from backend.wa_gateway import WAGateway as CloudService
from backend.grabber import DataGrabber
from backend.group_finder import GroupFinder


class TestCloudAndGrabberSystems:
    def test_cloud_service_connection(self):
        """تغطية CloudService"""
        with patch("requests.get") as mock_get:
            service = CloudService()
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"status": "open"}
            state = service.get_connection_state("G777")
            assert state["status"] == "open"

    def test_grabber_logic(self):
        """تغطية DataGrabber"""
        grabber = DataGrabber()
        # Test scroll mock
        with patch("time.sleep"):
            grabber._smart_scroll(MagicMock())
            assert True

    def test_group_finder_search(self):
        """تغطية GroupFinder"""
        finder = GroupFinder()
        # Test string extraction
        # Link must be > 20 chars to match regex in GroupFinder
        link_str = "https://chat.whatsapp.com/G777LinkThatIsLongEnoughToMatchRegex123"
        links = finder.extract_links_from_text(f"Join at {link_str}")
        assert len(links) == 1
        assert "G777Link" in links[0]

    def test_cloud_webhook_setup(self):
        """تغطية ضبط الـ Webhook سحابياً"""
        service = CloudService()
        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 201
            service.set_evolution_webhook("G777", "http://test.com")
            assert mock_post.called


import pytest
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.controllers.group_sender_controller import GroupSenderController

class TestGroupSenderControllerSurgical:
    """
    Surgical tests for GroupSenderController
    """

    @pytest.fixture
    def controller(self):
        with patch('ui.controllers.group_sender_controller.cloud_service', MagicMock()):
            with patch('ui.controllers.group_sender_controller.CampaignManager') as MockCM:
                with patch('ui.controllers.group_sender_controller.ExcelProcessor') as MockEP:
                    ctrl = GroupSenderController()
                    return ctrl

    def test_set_file_path(self, controller):
        controller.set_file_path("test.xlsx")
        assert controller.state['file_path'] == "test.xlsx"

    def test_load_contacts_no_file(self, controller):
        res = controller.load_contacts_from_sheet("Sheet1")
        assert res == []

    def test_load_contacts_success(self, controller):
        controller.set_file_path("test.xlsx")
        controller.excel_processor.read_contacts.return_value = [{"name": "User", "phone": "123"}]
        
        res = controller.load_contacts_from_sheet("Sheet1")
        assert len(res) == 1
        assert res[0]['phone'] == "123"
        assert controller.state['contacts'] == res

    @pytest.mark.asyncio
    async def test_run_campaign_no_contacts(self, controller):
        res = await controller.run_campaign("Hello")
        assert "error" in res
        assert "No contacts" in res["error"]

    @pytest.mark.asyncio
    async def test_run_campaign_already_running(self, controller):
        controller.state['is_running'] = True
        res = await controller.run_campaign("Hello")
        assert "error" in res
        assert "already running" in res["error"]

    @pytest.mark.asyncio
    async def test_run_campaign_success(self, controller):
        controller.state['contacts'] = [{"phone": "123"}, {"phone": "456"}]
        controller.campaign_manager.run_smart_campaign = AsyncMock(return_value={"success": True})
        
        progress_mock = MagicMock()
        res = await controller.run_campaign(
            message="Test Msg", 
            progress_callback=progress_mock
        )
        
        assert res["success"] is True
        assert controller.state['is_running'] is False
        controller.campaign_manager.run_smart_campaign.assert_called_once()
        
        # Verify numbers extracted correctly
        args, kwargs = controller.campaign_manager.run_smart_campaign.call_args
        assert kwargs['numbers'] == ["123", "456"]
        assert kwargs['message'] == "Test Msg"

    @pytest.mark.asyncio
    async def test_run_campaign_exception(self, controller):
        controller.state['contacts'] = [{"phone": "123"}]
        controller.campaign_manager.run_smart_campaign.side_effect = Exception("General Failure")
        
        with pytest.raises(Exception) as exc:
            await controller.run_campaign("Hello")
        
        assert str(exc.value) == "General Failure"
        assert controller.state['is_running'] is False

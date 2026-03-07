
import pytest
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.controllers.members_grabber_controller import MembersGrabberController

class TestMembersGrabberControllerSurgical:
    """
    Surgical tests for MembersGrabberController
    """

    @pytest.fixture
    def controller(self):
        with patch('ui.controllers.members_grabber_controller.cloud_service', MagicMock()):
            ctrl = MembersGrabberController()
            return ctrl

    @pytest.mark.asyncio
    async def test_fetch_groups_success_list(self, controller):
        with patch('ui.controllers.members_grabber_controller.cloud_service.fetch_all_groups') as mock_fetch:
            mock_fetch.return_value = [{"id": "123", "name": "Group 1"}, {"id": "456", "name": "Group 2"}]
            groups = await controller.fetch_groups()
            assert len(groups) == 2
            assert groups[0]['label'] == "Group 1"
            assert groups[1]['value'] == "456"

    @pytest.mark.asyncio
    async def test_fetch_groups_success_dict(self, controller):
        with patch('ui.controllers.members_grabber_controller.cloud_service.fetch_all_groups') as mock_fetch:
            mock_fetch.return_value = {"data": [{"id": "789", "name": "Group 3"}]}
            groups = await controller.fetch_groups()
            assert len(groups) == 1
            assert groups[0]['label'] == "Group 3"

    @pytest.mark.asyncio
    async def test_fetch_groups_failure(self, controller):
        with patch('ui.controllers.members_grabber_controller.cloud_service.fetch_all_groups') as mock_fetch:
            mock_fetch.side_effect = Exception("API Error")
            groups = await controller.fetch_groups()
            assert groups == []

    @pytest.mark.asyncio
    async def test_grab_members_success_nested(self, controller):
        with patch('ui.controllers.members_grabber_controller.cloud_service.fetch_group_participants') as mock_fetch:
            # Test complex nested structure handling
            mock_fetch.return_value = {
                "data": {
                    "participants": [
                        {"id": "201001234567@s.whatsapp.net", "admin": True},
                        {"id": "201007654321@s.whatsapp.net", "admin": False}
                    ]
                }
            }
            members = await controller.grab_members("jid")
            assert len(members) == 2
            assert members[0]['phone'] == "201001234567"
            assert members[0]['status'] == "Admin"
            assert members[1]['status'] == "Member"

    @pytest.mark.asyncio
    async def test_grab_members_is_loading_guard(self, controller):
        controller.state['is_loading'] = True
        members = await controller.grab_members("jid")
        assert members == []

    def test_export_to_excel_success(self, controller):
        controller.state['members'] = [{"name": "A", "phone": "123", "status": "Admin"}]
        with patch('pandas.DataFrame.to_excel') as mock_to_excel:
            path = controller.export_to_excel("test.xlsx")
            assert path == "test.xlsx"
            mock_to_excel.assert_called_once()

    def test_export_to_excel_no_data(self, controller):
        path = controller.export_to_excel()
        assert path is None

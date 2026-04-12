import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Mock User dependency override
def mock_get_current_user():
    return {"user_id": "test_user_id", "email": "test@example.com", "role": "admin"}

class TestGroupSender:
    def setup_method(self):
        # We need the app for TestClient
        from main import app
        from backend.core.auth import get_current_user
        
        # Override the dependency for ALL tests in this suite
        app.dependency_overrides[get_current_user] = mock_get_current_user
        self.client = TestClient(app)
        
    def teardown_method(self):
        from main import app
        # Reset overrides to avoid side effects on other tests
        app.dependency_overrides = {}

    @patch("backend.evolution.groups.GroupHandler.fetch_all_groups")
    @patch("backend.database_manager.execute_values")
    def test_fetch_groups_api_bulk(self, mock_exec_values, mock_fetch):
        """Should return a list of groups and call bulk sync logic."""
        mock_fetch.return_value = [
            {"id": "123@g.us", "subject": "Test Group 1"},
            {"id": "456@g.us", "subject": "Test Group 2"}
        ]
        
        # We must also mock the pool and connection to avoid real DB access
        from backend.database_manager import db_manager
        with patch.object(db_manager, 'get_connection') as mock_conn_get:
            mock_conn = MagicMock()
            mock_conn_get.return_value = mock_conn
            # Ensure pool is not None
            with patch.object(db_manager, 'pool', True):
                response = self.client.get(
                    "/api/groups/sync", 
                    headers={"X-Instance-Name": "test_instance"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert len(data["groups"]) == 2
                # Verify execute_values was called (Bulk Insert)
                assert mock_exec_values.called

    def test_broadcast_to_groups_validation(self):
        """Should fail if no groups or message are provided."""
        response = self.client.post(
            "/api/groups/broadcast", 
            json={}, 
            headers={"X-Instance-Name": "test_instance"}
        )
        # Authentication should succeed (mocked), but validation should fail
        assert response.status_code == 422 # Validation Error

    @patch("backend.evolution.groups.GroupHandler.fetch_all_groups")
    @patch("backend.database_manager.execute_values")
    def test_sync_groups_logic_bulk(self, mock_exec_values, mock_fetch):
        """Verify the service logic uses bulk upsert."""
        mock_fetch.return_value = [
            {"id": "123@g.us", "subject": "Test Group 1"}
        ]
        
        from backend.database_manager import db_manager
        with patch.object(db_manager, 'get_connection') as mock_conn_get:
            mock_conn = MagicMock()
            mock_conn_get.return_value = mock_conn
            with patch.object(db_manager, 'pool', True):
                from backend.services.group_sender_service import GroupSenderService
                service = GroupSenderService(instance_name="test_instance")
                result = service.sync_groups()
                
                assert len(result) == 1
                assert mock_exec_values.called

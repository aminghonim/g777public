
import pytest
from unittest.mock import MagicMock, patch, ANY
import sys
import os
import json
from datetime import datetime, timedelta

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db_service import (
    SettingsCache, get_tenant_settings, update_tenant_settings,
    get_system_prompt, get_all_offerings, create_offering, update_offering,
    get_customer_by_phone, create_customer, update_customer_profile,
    mark_field_collected, save_message, is_excluded, pause_bot_for_customer,
    get_training_samples
)

class TestDBServiceCoverage:
    """
    Surgical Coverage Test for backend/db_service.py
    """

    @pytest.fixture
    def mock_cursor(self):
        """Mock Database Cursor"""
        mock_cur = MagicMock()
        mock_cur.__enter__.return_value = mock_cur
        mock_cur.__exit__.return_value = None
        return mock_cur

    @pytest.fixture
    def mock_db(self, mock_cursor):
        """Mock get_db_cursor context manager"""
        with patch('backend.db_service.get_db_cursor') as mock_ctx:
            mock_ctx.return_value = mock_cursor
            yield mock_ctx

    def test_settings_cache(self):
        """Test Cache Logic"""
        cache = SettingsCache(ttl_seconds=1)
        cache.set("key", "val")
        assert cache.get("key") == "val"
        
        # Manually expire
        cache._timestamps["key"] = datetime.now() - timedelta(seconds=2)
        assert cache.get("key") is None
        
        cache.set("k2", "v2")
        cache.invalidate("k2")
        assert cache.get("k2") is None
        
        cache.set("k3", "v3")
        cache.invalidate()
        assert cache.get("k3") is None

    def test_get_tenant_settings(self, mock_db, mock_cursor):
        # Case 1: Cache Miss -> DB Hit
        with patch('backend.db_service.settings_cache') as mock_cache:
            mock_cache.get.return_value = None
            mock_cursor.fetchone.return_value = {'id': 1, 'name': 'G777'}
            
            res = get_tenant_settings()
            assert res['name'] == 'G777'
            mock_cache.set.assert_called_once()
            
    def test_update_tenant_settings(self, mock_db, mock_cursor):
        # Case 1: Valid Update
        res = update_tenant_settings({'name': 'NewName'})
        assert res is True
        mock_cursor.execute.assert_called_once()
        
        # Case 2: Empty Update
        res = update_tenant_settings({})
        assert res is False

    def test_system_prompt(self, mock_db, mock_cursor):
        with patch('backend.db_service.settings_cache') as mock_cache:
            mock_cache.get.return_value = None
            mock_cursor.fetchone.return_value = {'prompt_text': 'You are AI'}
            
            res = get_system_prompt('test')
            assert res == 'You are AI'

    def test_offerings_crud(self, mock_db, mock_cursor):
        # Create
        mock_cursor.fetchone.return_value = {'id': 99}
        res = create_offering({'name': 'Prod1'})
        assert res == "99"
        
        # Update
        res = update_offering(99, {'price': 50})
        assert res is True

    def test_customer_flow(self, mock_db, mock_cursor):
        # Get
        mock_cursor.fetchone.return_value = {'phone': '123', 'name': 'Test'}
        res = get_customer_by_phone('123')
        assert res['name'] == 'Test'
        
        # Create
        mock_cursor.fetchone.return_value = {'id': 'cust_1'}
        res = create_customer('123')
        assert res == "cust_1"
        
        # Update
        res = update_customer_profile('123', {'name': 'New'})
        assert res is True

    def test_field_collection(self, mock_db, mock_cursor):
        # Case: Field in missing list
        mock_cursor.fetchone.return_value = {'missing_fields': ['email', 'age']}
        res = mark_field_collected('123', 'email')
        assert res is True
        # Verify update call removed 'email'
        call_args = mock_cursor.execute.call_args_list[1]
        assert 'email' not in call_args[0][1][0] # The JSON Dump string
        
    def test_save_message(self, mock_db, mock_cursor):
        save_message('conv1', 'cust1', 'user', 'Hi')
        mock_cursor.execute.assert_called()
        
    def test_smart_pause_logic(self, mock_db, mock_cursor):
        """Test the logic for pausing/excluding bot"""
        # Case 1: Not Excluded
        mock_cursor.fetchone.return_value = None
        assert is_excluded("123") is False
        
        # Case 2: Explicitly Excluded via Tenant Settings
        with patch('backend.db_service.get_tenant_settings', return_value={'excluded_contacts': ['123']}):
            assert is_excluded("123") is True
            
        # Case 3: Blocked in DB
        mock_cursor.fetchone.return_value = {'is_blocked': True, 'bot_paused_until': None}
        assert is_excluded("123") is True
        
        # Case 4: Smart Pause Active
        future_time = datetime.now() + timedelta(hours=1)
        # Mocking fetchone result directly doesn't work well for datetimes across timezones sometimes 
        # so we ensure it returns a valid object
        mock_cursor.fetchone.return_value = {'is_blocked': False, 'bot_paused_until': future_time}
        assert is_excluded("123") is True
        
        # Case 5: Smart Pause Expired
        past_time = datetime.now() - timedelta(hours=1)
        mock_cursor.fetchone.return_value = {'is_blocked': False, 'bot_paused_until': past_time}
        assert is_excluded("123") is False

    def test_pause_bot_action(self, mock_db, mock_cursor):
        res = pause_bot_for_customer("123", hours=2)
        assert res is True
        # Check that update_customer_profile or execute was called with correct timestamp
        # The function calls create_customer first (upsert) then update
        assert mock_cursor.execute.call_count >= 2

    def test_training_samples(self, mock_db, mock_cursor):
        mock_cursor.fetchall.return_value = [
            {'question': 'Hi', 'humanized_response': 'Welcome'}
        ]
        res = get_training_samples()
        assert "Welcome" in res

if __name__ == "__main__":
    pytest.main([__file__])

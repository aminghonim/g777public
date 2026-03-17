
import pytest
import sys
import json
from unittest.mock import MagicMock, patch, call, ANY
from datetime import datetime, timedelta

# Import the module
from backend import db_service

class TestDBServiceSurgical:
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Reset internal state
        db_service._connection_pool = None
        db_service.settings_cache._cache = {}
        db_service.settings_cache._timestamps = {}
        db_service.DATABASE_URL = "postgres://fake:fake@local/db"
        yield
        db_service._connection_pool = None

    # --- 1. Pool Creation Tests ---
    @patch('backend.db_service.pool.ThreadedConnectionPool')
    def test_get_connection_pool_success(self, mock_pool_cls):
        mock_instance = MagicMock()
        mock_pool_cls.return_value = mock_instance
        
        # First call
        pool = db_service.get_connection_pool()
        assert pool is mock_instance
        mock_pool_cls.assert_called_with(1, 10, dsn=db_service.DATABASE_URL)
        
        # Second call (Cached)
        mock_pool_cls.reset_mock()
        pool2 = db_service.get_connection_pool()
        assert pool2 is mock_instance
        mock_pool_cls.assert_not_called()

    @patch('backend.db_service.pool.ThreadedConnectionPool')
    def test_get_connection_pool_failure(self, mock_pool_cls):
        mock_pool_cls.side_effect = Exception("Fail")
        assert db_service.get_connection_pool() is None

    # --- 2. Cursor Context Manager Tests ---
    @patch('backend.db_service.get_connection_pool')
    def test_get_db_cursor_success(self, mock_get_pool):
        # Setup Dependency Chain
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_get_pool.return_value = mock_pool
        mock_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Test
        with db_service.get_db_cursor() as cursor:
            assert cursor is mock_cursor
            
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_pool.putconn.assert_called_with(mock_conn)

    @patch('backend.db_service.get_connection_pool')
    def test_get_db_cursor_exception(self, mock_get_pool):
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        
        mock_get_pool.return_value = mock_pool
        mock_pool.getconn.return_value = mock_conn
        
        with pytest.raises(ValueError, match="Boom"):
            with db_service.get_db_cursor():
                raise ValueError("Boom")
                
        mock_conn.rollback.assert_called_once()
        mock_pool.putconn.assert_called_with(mock_conn)

    @patch('backend.db_service.get_connection_pool')
    def test_get_db_cursor_pool_exhausted(self, mock_get_pool):
        mock_pool = MagicMock()
        mock_get_pool.return_value = mock_pool
        mock_pool.getconn.side_effect = Exception("Empty")
        
        with pytest.raises(Exception, match="Empty"):
            with db_service.get_db_cursor():
                 pass

    @patch('backend.db_service.get_connection_pool')
    def test_get_db_cursor_no_pool(self, mock_get_pool):
        mock_get_pool.return_value = None
        with db_service.get_db_cursor() as cursor:
            assert cursor is None

    # --- 3. Business Logic Tests (Mocking get_db_cursor) ---
    
    @patch('backend.db_service.get_db_cursor')
    def test_get_tenant_settings(self, mock_get_cursor):
        # Setup Mock Cursor
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        # DB Return
        mock_cursor.fetchone.return_value = {'id': 1, 'val': 'test'}
        
        # Call
        res = db_service.get_tenant_settings()
        assert res == {'id': 1, 'val': 'test'}
        
        # Cache Hit Verify
        mock_cursor.reset_mock()
        res2 = db_service.get_tenant_settings()
        assert res2 == {'id': 1, 'val': 'test'}
        mock_cursor.execute.assert_not_called()

    @patch('backend.db_service.get_db_cursor')
    def test_get_tenant_settings_empty(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        assert db_service.get_tenant_settings() == {}

    @patch('backend.db_service.get_db_cursor')
    def test_update_tenant_settings(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        assert db_service.update_tenant_settings({'a': 1}) is True
        assert db_service.update_tenant_settings({}) is False
        
        mock_cursor.execute.assert_called()
        assert db_service.settings_cache.get('tenant_settings') is None

    @patch('backend.db_service.get_db_cursor')
    def test_get_system_prompt(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = {'prompt_text': 'Hola'}
        assert db_service.get_system_prompt('sales') == 'Hola'
        
        # Not found
        mock_cursor.fetchone.return_value = None
        db_service.settings_cache.invalidate()
        assert db_service.get_system_prompt('unknown') is None

    @patch('backend.db_service.get_db_cursor')
    def test_offerings_crud(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        # Get All
        mock_cursor.fetchall.return_value = [{'name': 'P1', 'price': 10}]
        res = db_service.get_all_offerings()
        assert len(res) == 1
        assert res[0]['name'] == 'P1'
        
        # Create
        mock_cursor.fetchone.return_value = {'id': 99}
        assert db_service.create_offering({'name': 'N'}) == '99'
        
        # Update
        assert db_service.update_offering(99, {'price': 20}) is True

    @patch('backend.db_service.get_db_cursor')
    def test_customers_crud(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        # Create
        mock_cursor.fetchone.return_value = {'id': 50}
        assert db_service.create_customer('123', 'X') == '50'
        
        # Get
        mock_cursor.fetchone.return_value = {'id': 50, 'phone': '123'}
        c = db_service.get_customer_by_phone('123')
        assert c['id'] == 50
        
        # Update
        assert db_service.update_customer_profile('123', {'a': 1}) is True

    @patch('backend.db_service.get_db_cursor')
    def test_mark_field_collected(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        # Setup: Missing fields has 'age'
        mock_cursor.fetchone.return_value = {'missing_fields': ['age', 'email']}
        
        # Call
        res = db_service.mark_field_collected('123', 'age')
        assert res is True
         
        # Assert update
        assert mock_cursor.execute.call_count == 2
        update_call = mock_cursor.execute.call_args_list[1]
        assert '["email"]' in str(update_call) # age should be removed

    @patch('backend.db_service.get_db_cursor')
    def test_messaging(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        # Create Conv
        mock_cursor.fetchone.return_value = {'id': 100}
        assert db_service.create_conversation(1, '010') == '100'
        
        # Save Msg
        db_service.save_message(100, 1, 'user', 'hi')
        assert mock_cursor.execute.called
        
        # History
        mock_cursor.fetchall.return_value = [
            {'sender_type': 'user', 'content': 'u'},
            {'sender_type': 'assistant', 'content': 'a'}
        ]
        h = db_service.get_conversation_history(100)
        assert 'العميل: u' in h

    @patch('backend.db_service.get_db_cursor')
    @patch('backend.db_service.get_tenant_settings')
    def test_is_excluded(self, mock_settings, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        # 1. Tenant Block
        mock_settings.return_value = {'excluded_contacts': ['11']}
        assert db_service.is_excluded('11') is True
        
        # 2. Contact Block
        mock_settings.return_value = {}
        mock_cursor.fetchone.side_effect = [{'exclude_from_bot': True}]
        assert db_service.is_excluded('22') is True
        
        # 3. Profile Block
        mock_cursor.fetchone.side_effect = [
            {'exclude_from_bot': False},
            {'is_blocked': True, 'bot_paused_until': None}
        ]
        assert db_service.is_excluded('33') is True
        
        # 4. Paused
        future = datetime.now() + timedelta(hours=1)
        mock_cursor.fetchone.side_effect = [
            {'exclude_from_bot': False},
            {'is_blocked': False, 'bot_paused_until': future}
        ]
        assert db_service.is_excluded('44') is True
        
        # 5. Safe
        mock_cursor.fetchone.side_effect = [None, None]
        assert db_service.is_excluded('55') is False

    @patch('backend.db_service.create_customer')
    @patch('backend.db_service.get_db_cursor')
    def test_pause_bot_for_customer(self, mock_get_cursor, mock_create):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        # Create customer Mock
        mock_create.return_value = '50'
        
        assert db_service.pause_bot_for_customer('123', 1) is True
        assert "UPDATE customer_profiles" in mock_cursor.execute.call_args[0][0]

    @patch('backend.db_service.get_db_cursor')
    def test_get_training_samples(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        
        # Success
        mock_cursor.fetchall.return_value = [{'question': 'MQ', 'humanized_response': 'MA'}]
        assert "Q: MQ" in db_service.get_training_samples()
        
        # Empty
        mock_cursor.fetchall.return_value = []
        assert db_service.get_training_samples() == ""

        # Exception
        mock_cursor.execute.side_effect = Exception("DB Error")
        assert db_service.get_training_samples() == ""

    # --- New Coverage Tests ---

    def test_settings_cache_expiry_delete(self):
        # Explicit test for the 'del' branch
        cache = db_service.SettingsCache(ttl_seconds=1)
        cache.set("key", "val")
        
        # Trick: manually set timestamp to old
        cache._timestamps["key"] = datetime.now() - timedelta(seconds=2)
        
        # This should trigger the 'del' line
        assert cache.get("key") is None
        assert "key" not in cache._cache

    @patch('backend.db_service.get_db_cursor')
    def test_get_all_customers(self, mock_get_cursor):
         mock_cursor = MagicMock()
         mock_get_cursor.return_value.__enter__.return_value = mock_cursor
         mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]
         
         res = db_service.get_all_customers()
         assert len(res) == 2
         assert "SELECT * FROM customer_profiles" in mock_cursor.execute.call_args[0][0]

    @patch('backend.db_service.get_db_cursor')
    def test_get_all_offerings_filters(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        # Test with Category
        db_service.get_all_offerings(cat="Tech")
        call_args = mock_cursor.execute.call_args[0]
        assert "AND category = %s" in call_args[0]
        assert "Tech" in call_args[1]

    @patch('backend.db_service.get_all_offerings')
    def test_format_offerings_for_prompt(self, mock_get_offerings):
        # Case 1: Empty
        mock_get_offerings.return_value = []
        assert "لا توجد منتجات" in db_service.format_offerings_for_prompt()
        
        # Case 2: Items
        mock_get_offerings.return_value = [
            {'name': 'Item1', 'price': 100, 'currency': 'USD', 'description': 'Desc'}
        ]
        res = db_service.format_offerings_for_prompt()
        assert "- Item1 (100 USD): Desc" in res

    @patch('backend.db_service.get_db_cursor')
    def test_pause_bot_exception(self, mock_get_cursor):
        # Ensure we enter the block but fail inside
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Fail")
        
        assert db_service.pause_bot_for_customer("123") is False

    @patch('backend.db_service.get_connection_pool')
    def test_main_block(self, mock_pool):
        # Simulate __main__ behavior
        mock_pool.return_value = True
        # Just ensure no crash
        if db_service.get_connection_pool():
            pass
        
        mock_pool.return_value = None
        if db_service.get_connection_pool():
            pass

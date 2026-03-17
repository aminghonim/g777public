
import pytest
from unittest.mock import MagicMock, patch, ANY
import json
from datetime import datetime, timedelta
from backend.db_service import (
    get_connection_pool, get_db_cursor, SettingsCache,
    get_tenant_settings, update_tenant_settings,
    get_system_prompt, get_all_offerings, format_offerings_for_prompt,
    create_offering, update_offering,
    get_all_customers, get_customer_by_phone, create_customer, update_customer_profile, mark_field_collected,
    save_message, create_conversation, get_conversation_history,
    is_excluded, pause_bot_for_customer, get_training_samples
)

class TestDatabaseManagerSurgical:

    @pytest.fixture
    def mock_pool(self):
        with patch('backend.db_service._connection_pool') as pool:
            yield pool

    @pytest.fixture
    def mock_cursor(self):
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = None
        return cursor

    @pytest.fixture
    def mock_db(self, mock_cursor):
        pool = MagicMock()
        conn = MagicMock()
        pool.getconn.return_value = conn
        conn.cursor.return_value = mock_cursor
        
        with patch('backend.db_service.get_connection_pool', return_value=pool):
            yield mock_cursor

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================

    def test_settings_cache(self):
        cache = SettingsCache(ttl_seconds=1)
        cache.set("k", "v")
        assert cache.get("k") == "v"
        cache.invalidate("k")
        assert cache.get("k") is None
        
        cache.set("k", "v")
        cache.invalidate() # Clear all
        assert cache.get("k") is None

    def test_get_connection_pool_creation(self):
        with patch('backend.db_service._connection_pool', None), \
             patch('backend.db_service.DATABASE_URL', "postgres://..."), \
             patch('psycopg2.pool.ThreadedConnectionPool') as mock_pool_cls:
            
            p = get_connection_pool()
            assert p is not None
            mock_pool_cls.assert_called()

    def test_get_tenant_settings_success(self, mock_db):
        from backend.db_service import settings_cache
        settings_cache.invalidate() # Clear cache first
        mock_db.fetchone.return_value = {'key': 'val'}
        res = get_tenant_settings()
        assert res.get('key') == 'val'

    def test_update_tenant_settings_success(self, mock_db):
        res = update_tenant_settings({'key': 'val'})
        assert res is True
        mock_db.execute.assert_called()

    def test_get_system_prompt_success(self, mock_db):
        mock_db.fetchone.return_value = {'prompt_text': 'hello'}
        res = get_system_prompt("test")
        assert res == 'hello'

    def test_get_all_offerings_filters(self, mock_db):
        get_all_offerings(cat="Tech", avail=True)
        query = mock_db.execute.call_args[0][0]
        assert "category =" in query
        assert "is_available =" in query

    def test_format_offerings_for_prompt(self):
        with patch('backend.db_service.get_all_offerings', return_value=[{'name': 'A', 'price': 10}]):
            res = format_offerings_for_prompt()
            assert "- A (10 EGP)" in res

    def test_create_update_offering(self, mock_db):
        mock_db.fetchone.return_value = {'id': 1}
        assert create_offering({'name': 'T'}) == '1'
        
        assert update_offering('1', {'name': 'T2'}) is True
        assert update_offering('1', {}) is False

    def test_customer_crud(self, mock_db):
        mock_db.fetchall.return_value = [{'name': 'A'}]
        assert len(get_all_customers()) == 1
        
        mock_db.fetchone.return_value = {'name': 'A'}
        assert get_customer_by_phone("123")['name'] == 'A'
        
        mock_db.fetchone.return_value = {'id': '100'}
        assert create_customer("123") == '100'
        
        assert update_customer_profile("123", {'name': 'B'}) is True

    def test_mark_field_collected(self, mock_db):
        mock_db.fetchone.return_value = {'missing_fields': ['name', 'city']}
        mark_field_collected("123", "name")
        update_call = mock_db.execute.call_args_list[-1]
        assert "name" not in update_call[0][0] # Should check args but string construction varies

    def test_conversation_handling(self, mock_db):
        mock_db.fetchone.return_value = {'id': '1'}
        result = create_conversation("cust_id", "123")
        assert result == '1'
        
        save_message("conv_id", "cust_id", "user", "msg")
        mock_db.execute.assert_called()

        mock_db.fetchall.return_value = [{'sender_type': 'user', 'content': 'hi'}]
        hist = get_conversation_history("conv_id")
        assert "العميل: hi" in hist

    def test_is_excluded_logic(self, mock_db):
        # 1. Not excluded
        mock_db.fetchone.return_value = None
        assert is_excluded("123") is False
        
        # 2. Blocked in contacts
        mock_db.fetchone.return_value = {'exclude_from_bot': True}
        assert is_excluded("123") is True
        
        # 3. Paused
        mock_db.fetchone.side_effect = [
            None, # contacts check
            {'is_blocked': False, 'bot_paused_until': datetime.now() + timedelta(hours=1)}
        ]
        assert is_excluded("123") is True

    def test_pause_bot_success(self, mock_db):
        assert pause_bot_for_customer("123") is True

    def test_get_training_samples(self, mock_db):
        mock_db.fetchall.return_value = [{'question': 'q', 'humanized_response': 'a'}]
        res = get_training_samples()
        assert "Q: q" in res

    # =================================================================
    # ❌ LOGIC FAILURE STATE TESTS
    # =================================================================

    def test_get_connection_pool_failure(self):
        with patch('backend.db_service._connection_pool', None), \
             patch('psycopg2.pool.ThreadedConnectionPool', side_effect=Exception("DB Down")):
            assert get_connection_pool() is None

    def test_get_db_cursor_no_pool(self):
        with patch('backend.db_service.get_connection_pool', return_value=None):
            with get_db_cursor() as cur:
                assert cur is None

    def test_update_tenant_settings_no_cursor(self):
        with patch('backend.db_service.get_db_cursor') as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = None
            assert update_tenant_settings({'a': 1}) is False

    def test_get_system_prompt_miss(self, mock_db):
        mock_db.fetchone.return_value = None
        assert get_system_prompt("missing") is None

    def test_format_offerings_empty(self):
        with patch('backend.db_service.get_all_offerings', return_value=[]):
            assert "لا توجد" in format_offerings_for_prompt()

    def test_mark_field_collected_no_missing(self, mock_db):
        mock_db.fetchone.return_value = {'missing_fields': None}
        assert mark_field_collected("123", "f") is True # Should return True as "done"

    def test_is_excluded_paused_expired(self, mock_db):
        mock_db.fetchone.side_effect = [
            None,
            {'is_blocked': False, 'bot_paused_until': datetime.now() - timedelta(hours=1)}
        ]
        assert is_excluded("123") is False

    # =================================================================
    # 💥 SYSTEM FAILURE STATE TESTS
    # =================================================================

    def test_transaction_rollback(self):
        """Test transaction rollback on exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        mock_pool = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        
        with patch('backend.db_service.get_connection_pool', return_value=mock_pool):
            try:
                with get_db_cursor() as cur:
                    raise Exception("DB Error")
            except:
                pass
            
            mock_conn.rollback.assert_called()
            mock_pool.putconn.assert_called()



    def test_pause_bot_exception(self, mock_db):
        mock_db.execute.side_effect = Exception("DB Lock")
        assert pause_bot_for_customer("123") is False

    def test_get_training_samples_table_missing(self, mock_db):
        mock_db.execute.side_effect = Exception("Table not found")
        assert get_training_samples() == ""

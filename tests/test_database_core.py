import pytest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database_manager import DatabaseManager


class TestDatabaseManager:
    @pytest.fixture
    def db_manager(self):
        # Mock the environment variable and connection pool
        with patch.dict(
            os.environ, {"DATABASE_URL": "postgres://user:pass@localhost:5432/testdb"}
        ):
            with patch("psycopg2.pool.SimpleConnectionPool") as mock_pool:
                manager = DatabaseManager()
                manager.pool = mock_pool.return_value
                yield manager

    def test_init_connection_success(self):
        """Test successful database initialization"""
        with patch.dict(
            os.environ, {"DATABASE_URL": "postgres://real:db@host:5432/db"}
        ):
            with patch("psycopg2.pool.SimpleConnectionPool") as mock_pool:
                db = DatabaseManager()
                assert db.pool is not None
                mock_pool.assert_called_once()

    def test_upsert_customer_new(self, db_manager):
        """Test creating a new customer"""
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        db_manager.pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Simulate "Active Customer Not Found" first (fetching None)
        mock_cursor.fetchone.return_value = None
        # Then simulate INSERT returning an ID
        mock_cursor.fetchone.side_effect = [None, {"id": "new-uuid-123"}]

        cust_id = db_manager.upsert_customer(
            "201000000000", "test_user", name="New User"
        )

        assert cust_id == "new-uuid-123"
        assert mock_cursor.execute.call_count == 2  # 1 Select, 1 Insert

    def test_upsert_customer_existing(self, db_manager):
        """Test updating an existing customer"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        db_manager.pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Simulate Found Customer
        mock_cursor.fetchone.return_value = {"id": "existing-uuid-999", "metadata": {}}

        cust_id = db_manager.upsert_customer(
            "201000000000", "test_user", name="Update User"
        )

        assert cust_id == "existing-uuid-999"
        assert "UPDATE customers SET" in mock_cursor.execute.call_args_list[1][0][0]

    def test_save_interaction(self, db_manager):
        """Test saving a chat message"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        db_manager.pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {"id": "msg-uuid-777"}

        msg_id = db_manager.save_interaction(
            "cust-1", "test_user", "user", "Hello"
        )

        assert msg_id == "msg-uuid-777"
        mock_cursor.execute.assert_called()

    def test_get_customer_history(self, db_manager):
        """Test retrieving chat history"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        db_manager.pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {"role": "user", "message": "hi", "timestamp": datetime.now()},
            {"role": "assistant", "message": "hello", "timestamp": datetime.now()},
        ]

        history = db_manager.get_customer_interactions("cust-1", "test_user")
        assert len(history) == 2
        assert history[0]["role"] == "user"


if __name__ == "__main__":
    pytest.main([__file__])

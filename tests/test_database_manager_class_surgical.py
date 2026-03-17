"""
Surgical Tests for backend/database_manager.py (DatabaseManager class)
======================================================================
Tests to increase coverage from 24% to 90%+
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime
from psycopg2.extras import Json


class TestDatabaseManagerClassSurgical:
    """Tests for DatabaseManager class in backend/database_manager.py"""

    @pytest.fixture
    def mock_pool(self):
        """Create a mock connection pool"""
        pool = MagicMock()
        conn = MagicMock()
        cursor = MagicMock()

        pool.getconn.return_value = conn
        conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
        conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        return pool, conn, cursor

    # =================================================================
    # ✅ INIT & POOL TESTS
    # =================================================================

    def test_init_success(self, mock_pool):
        """Test successful DatabaseManager initialization"""
        pool, conn, cursor = mock_pool

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            assert db.pool is not None

    def test_init_mock_mode(self):
        """Test mock mode when DATABASE_URL starts with 'mock://'"""
        with patch.dict("os.environ", {"DATABASE_URL": "mock://localhost"}):
            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            assert db.pool is None

    def test_init_sqlite_mode(self):
        """Test mock mode when DATABASE_URL starts with 'sqlite'"""
        with patch.dict("os.environ", {"DATABASE_URL": "sqlite:///test.db"}):
            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            assert db.pool is None

    def test_init_no_database_url(self):
        """Test ValueError when DATABASE_URL is missing"""
        with patch.dict("os.environ", {"DATABASE_URL": ""}):
            from backend.database_manager import DatabaseManager

            with pytest.raises(ValueError, match="DATABASE_URL not found"):
                DatabaseManager()

    def test_init_connection_failure(self):
        """Test exception propagation on connection failure"""
        with patch.dict("os.environ", {"DATABASE_URL": "postgres://fail"}), patch(
            "psycopg2.pool.SimpleConnectionPool",
            side_effect=Exception("Connection refused"),
        ):

            from backend.database_manager import DatabaseManager

            with pytest.raises(Exception, match="Connection refused"):
                DatabaseManager()

    # =================================================================
    # ✅ CONNECTION MANAGEMENT TESTS
    # =================================================================

    def test_get_connection_success(self, mock_pool):
        """Test getting connection from pool"""
        pool, conn, cursor = mock_pool

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.get_connection()

            pool.getconn.assert_called_once()
            assert result == conn

    def test_get_connection_no_pool(self):
        """Test get_connection returns None when pool is None"""
        with patch.dict("os.environ", {"DATABASE_URL": "mock://localhost"}):
            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            assert db.get_connection() is None

    def test_release_connection_success(self, mock_pool):
        """Test releasing connection back to pool"""
        pool, conn, cursor = mock_pool

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            db.release_connection(conn)
            pool.putconn.assert_called_once_with(conn)

    def test_release_connection_no_pool(self):
        """Test release_connection does nothing when pool is None"""
        with patch.dict("os.environ", {"DATABASE_URL": "mock://localhost"}):
            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            db.release_connection(MagicMock())  # Should not raise

    # =================================================================
    # ✅ UPSERT CUSTOMER TESTS
    # =================================================================

    def test_upsert_customer_mock_mode(self):
        """Test upsert_customer returns mock ID in mock mode"""
        with patch.dict("os.environ", {"DATABASE_URL": "mock://localhost"}):
            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.upsert_customer("+1234567890", "test_user", "Test User")
            assert result == "mock-customer-id"

    def test_upsert_customer_insert_new(self, mock_pool):
        """Test inserting a new customer"""
        pool, conn, cursor = mock_pool
        cursor.fetchone.side_effect = [
            None,
            {"id": "new-uuid-123"},
        ]  # First check returns None, then insert returns ID

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.upsert_customer(
                "+1234567890", "test_user", "New User", {"tier": "gold"}
            )

            assert result == "new-uuid-123"
            conn.commit.assert_called_once()

    def test_upsert_customer_update_existing(self, mock_pool):
        """Test updating an existing customer"""
        pool, conn, cursor = mock_pool
        cursor.fetchone.return_value = {
            "id": "existing-uuid",
            "metadata": {"tier": "silver"},
        }

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.upsert_customer(
                "+1234567890", "test_user", "Updated Name", {"tier": "gold"}
            )

            assert result == "existing-uuid"
            conn.commit.assert_called_once()

    def test_upsert_customer_update_name_only(self, mock_pool):
        """Test updating only the name of existing customer"""
        pool, conn, cursor = mock_pool
        cursor.fetchone.return_value = {"id": "existing-uuid", "metadata": None}

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.upsert_customer("+1234567890", "test_user", "New Name")

            assert result == "existing-uuid"

    def test_upsert_customer_exception_rollback(self, mock_pool):
        """Test rollback on exception during upsert"""
        pool, conn, cursor = mock_pool
        cursor.fetchone.side_effect = Exception("DB Error")

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()

            with pytest.raises(Exception, match="DB Error"):
                db.upsert_customer("+1234567890", "test_user", "Test")

            conn.rollback.assert_called_once()

    # =================================================================
    # ✅ SAVE INTERACTION TESTS
    # =================================================================

    def test_save_interaction_mock_mode(self):
        """Test save_interaction returns mock ID in mock mode"""
        with patch.dict("os.environ", {"DATABASE_URL": "mock://localhost"}):
            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.save_interaction("cust-id", "test_user", "user", "Hello!")
            assert result == "mock-interaction-id"

    def test_save_interaction_success(self, mock_pool):
        """Test saving interaction successfully"""
        pool, conn, cursor = mock_pool
        cursor.fetchone.return_value = {"id": "interaction-uuid"}

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.save_interaction(
                "cust-123", "test_user", "assistant", "How can I help?"
            )

            assert result == "interaction-uuid"
            conn.commit.assert_called_once()

    def test_save_interaction_exception_rollback(self, mock_pool):
        """Test rollback on exception during save_interaction"""
        pool, conn, cursor = mock_pool
        cursor.execute.side_effect = Exception("Insert failed")

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()

            with pytest.raises(Exception, match="Insert failed"):
                db.save_interaction("cust-123", "test_user", "user", "message")

            conn.rollback.assert_called_once()

    # =================================================================
    # ✅ SAVE ANALYTICS TESTS
    # =================================================================

    def test_save_analytics_mock_mode(self):
        """Test save_analytics returns mock ID in mock mode"""
        with patch.dict("os.environ", {"DATABASE_URL": "mock://localhost"}):
            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.save_analytics("cust-id", "test_user", "inquiry", 0.95)
            assert result == "mock-analytics-id"

    def test_save_analytics_success(self, mock_pool):
        """Test saving analytics successfully"""
        pool, conn, cursor = mock_pool
        cursor.fetchone.return_value = {"id": "analytics-uuid"}

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.save_analytics(
                "cust-123",
                "test_user",
                "booking",
                0.87,
                {"destination": "Egypt"},
            )

            assert result == "analytics-uuid"
            conn.commit.assert_called_once()

    def test_save_analytics_exception_rollback(self, mock_pool):
        """Test rollback on exception during save_analytics"""
        pool, conn, cursor = mock_pool
        cursor.execute.side_effect = Exception("Analytics insert failed")

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()

            with pytest.raises(Exception, match="Analytics insert failed"):
                db.save_analytics("cust-123", "test_user", "intent", 0.5)

            conn.rollback.assert_called_once()

    # =================================================================
    # ✅ GET CUSTOMER BY PHONE TESTS
    # =================================================================

    def test_get_customer_by_phone_mock_mode(self):
        """Test get_customer_by_phone returns None in mock mode"""
        with patch.dict("os.environ", {"DATABASE_URL": "mock://localhost"}):
            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.get_customer_by_phone("+1234567890", "test_user")
            assert result is None

    def test_get_customer_by_phone_found(self, mock_pool):
        """Test finding a customer by phone"""
        pool, conn, cursor = mock_pool
        cursor.fetchone.return_value = {
            "id": "uuid",
            "name": "Ahmed",
            "phone": "+201234567890",
        }

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.get_customer_by_phone("+201234567890", "test_user")

            assert result is not None
            assert result["name"] == "Ahmed"

    def test_get_customer_by_phone_not_found(self, mock_pool):
        """Test when customer is not found"""
        pool, conn, cursor = mock_pool
        cursor.fetchone.return_value = None

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.get_customer_by_phone("+999999999", "test_user")

            assert result is None

    # =================================================================
    # ✅ GET CUSTOMER INTERACTIONS TESTS
    # =================================================================

    def test_get_customer_interactions_mock_mode(self):
        """Test get_customer_interactions returns empty list in mock mode"""
        with patch.dict("os.environ", {"DATABASE_URL": "mock://localhost"}):
            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.get_customer_interactions("cust-id", "test_user")
            assert result == []

    def test_get_customer_interactions_success(self, mock_pool):
        """Test getting customer interactions"""
        pool, conn, cursor = mock_pool
        cursor.fetchall.return_value = [
            {"role": "user", "message": "Hi", "timestamp": datetime.now()},
            {"role": "assistant", "message": "Hello!", "timestamp": datetime.now()},
        ]

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            result = db.get_customer_interactions("cust-123", "test_user", limit=10)

            assert len(result) == 2
            assert result[0]["role"] == "user"

    # =================================================================
    # ✅ CLOSE TESTS
    # =================================================================

    def test_close_with_pool(self, mock_pool):
        """Test closing database connections"""
        pool, conn, cursor = mock_pool

        with patch.dict(
            "os.environ", {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        ), patch("psycopg2.pool.SimpleConnectionPool", return_value=pool):

            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            db.close()

            pool.closeall.assert_called_once()

    def test_close_no_pool(self):
        """Test close does nothing when pool is None"""
        with patch.dict("os.environ", {"DATABASE_URL": "mock://localhost"}):
            from backend.database_manager import DatabaseManager

            db = DatabaseManager()
            db.close()  # Should not raise

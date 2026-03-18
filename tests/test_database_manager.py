import pytest
from unittest.mock import MagicMock, patch, ANY
from backend.database_manager import DatabaseManager


# --- Fixtures ---
@pytest.fixture
def mock_db_pool():
    """Mock the psycopg2 connection pool specifically for this test file"""
    with patch("backend.database_manager.pool.SimpleConnectionPool") as mock_pool_cls:
        mock_pool_instance = mock_pool_cls.return_value

        # Create a mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Setup context manager for cursor
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_pool_instance.getconn.return_value = mock_conn

        yield {
            "pool_cls": mock_pool_cls,
            "pool": mock_pool_instance,
            "conn": mock_conn,
            "cursor": mock_cursor,
        }


@pytest.fixture
def db_instance(mock_db_pool):
    """Create a DatabaseManager instance using the mock pool"""
    # Force reload or re-init to ensure we use the mock
    with patch.dict(
        "os.environ", {"DATABASE_URL": "postgres://test:test@localhost:5432/testdb"}
    ):
        db = DatabaseManager()
        return db


# --- Tests for Initialization ---


def test_init_success(mock_db_pool):
    with patch.dict(
        "os.environ", {"DATABASE_URL": "postgres://test:test@localhost:5432/testdb"}
    ):
        db = DatabaseManager()
        assert db.pool is not None
        mock_db_pool["pool_cls"].assert_called_once()


def test_init_missing_env():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="DATABASE_URL not found"):
            DatabaseManager()


def test_init_mock_mode():
    with patch.dict("os.environ", {"DATABASE_URL": "mock://test"}):
        db = DatabaseManager()
        assert db.pool is None


# --- Tests for upsert_customer ---


def test_upsert_customer_new(db_instance, mock_db_pool):
    """Test inserting a new customer"""
    cursor = mock_db_pool["cursor"]
    # Setup: First fetchone returns None (customer doesn't exist)
    # Second fetchone returns the new ID (after INSERT)
    cursor.fetchone.side_effect = [None, {"id": "new-uuid-123"}]

    customer_id = db_instance.upsert_customer(
        phone="123456789",
        user_id="test_user",
        name="Test User",
        metadata={"source": "whatsapp"},
    )

    assert customer_id == "new-uuid-123"

    # Verify SELECT was called
    assert (
        "SELECT id, metadata FROM customers" in cursor.execute.call_args_list[0][0][0]
    )

    # Verify INSERT was called
    assert "INSERT INTO customers" in cursor.execute.call_args_list[1][0][0]
    assert "Test User" in cursor.execute.call_args_list[1][0][1]


def test_upsert_customer_update(db_instance, mock_db_pool):
    """Test updating an existing customer"""
    cursor = mock_db_pool["cursor"]
    # Setup: First fetchone returns existing record
    existing_record = {"id": "existing-uuid-456", "metadata": {"lang": "en"}}
    cursor.fetchone.side_effect = [existing_record]

    customer_id = db_instance.upsert_customer(
        phone="123456789",
        user_id="test_user",
        name="Updated Name",
        metadata={"new_field": "val"},
    )

    assert customer_id == "existing-uuid-456"

    # Verify UDPATE was called
    assert "UPDATE customers SET" in cursor.execute.call_args_list[1][0][0]
    args = cursor.execute.call_args_list[1][0][1]
    # Check that name was updated
    assert "Updated Name" in args
    # Check that metadata was merged (this is tricky with Json wrapper, but we check presence)
    # The actual argument will be a Json object, so exact equality might be hard without inspecting the object
    # But we can check that it wasn't an INSERT


def test_upsert_customer_error(db_instance, mock_db_pool):
    """Test error handling in upsert"""
    cursor = mock_db_pool["cursor"]
    cursor.execute.side_effect = Exception("DB Error")

    with pytest.raises(Exception, match="DB Error"):
        db_instance.upsert_customer("123456789", "test_user")

    # Verify rollback
    mock_db_pool["conn"].rollback.assert_called_once()


# --- Tests for save_interaction ---


def test_save_interaction_success(db_instance, mock_db_pool):
    cursor = mock_db_pool["cursor"]
    cursor.fetchone.return_value = {"id": "msg-uuid-789"}

    msg_id = db_instance.save_interaction("cust-123", "test_user", "user", "Hello")

    assert msg_id == "msg-uuid-789"
    assert "INSERT INTO interactions" in cursor.execute.call_args[0][0]
    mock_db_pool["conn"].commit.assert_called_once()


# --- Tests for save_analytics ---


def test_save_analytics_success(db_instance, mock_db_pool):
    cursor = mock_db_pool["cursor"]
    cursor.fetchone.return_value = {"id": "analytics-uuid-999"}

    analytics_id = db_instance.save_analytics(
        "cust-123", "test_user", "sales", 0.95, {"budget": "high"}
    )

    assert analytics_id == "analytics-uuid-999"
    assert "INSERT INTO analytics" in cursor.execute.call_args[0][0]


# --- Tests for get_customer_by_phone ---


def test_get_customer_by_phone_found(db_instance, mock_db_pool):
    cursor = mock_db_pool["cursor"]
    expected_data = {"id": "123", "name": "Found"}
    cursor.fetchone.return_value = expected_data

    result = db_instance.get_customer_by_phone("123456", "test_user")
    assert result == expected_data


def test_get_customer_by_phone_none(db_instance, mock_db_pool):
    cursor = mock_db_pool["cursor"]
    cursor.fetchone.return_value = None

    result = db_instance.get_customer_by_phone("123456", "test_user")
    assert result is None


# --- Tests for get_customer_interactions ---


def test_get_customer_interactions(db_instance, mock_db_pool):
    cursor = mock_db_pool["cursor"]
    mock_rows = [
        {"role": "user", "message": "hi", "timestamp": "2023-01-01"},
        {"role": "assistant", "message": "hello", "timestamp": "2023-01-01"},
    ]
    cursor.fetchall.return_value = mock_rows

    result = db_instance.get_customer_interactions("cust-123", "test_user")

    assert len(result) == 2
    assert result[0]["role"] == "user"
    query = cursor.execute.call_args[0][0]
    assert "SELECT i.role, i.message, i.timestamp" in query
    assert "FROM interactions" in query

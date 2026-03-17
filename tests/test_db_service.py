
import pytest
from unittest.mock import MagicMock, patch
from backend import db_service

@pytest.fixture
def mock_cursor_context():
    """Mock the get_db_cursor context manager"""
    with patch('backend.db_service.get_db_cursor') as mock_ctx:
        mock_cursor = MagicMock()
        mock_ctx.return_value.__enter__.return_value = mock_cursor
        yield mock_cursor

def test_get_tenant_settings_cached():
    """Test retrieving settings from cache"""
    db_service.settings_cache.set("tenant_settings", {"key": "val"})
    settings = db_service.get_tenant_settings()
    assert settings == {"key": "val"}

def test_get_tenant_settings_db(mock_cursor_context):
    """Test retrieving settings from DB when cache is empty"""
    db_service.settings_cache.invalidate("tenant_settings")
    mock_cursor_context.fetchone.return_value = {"key": "db_val"}
    
    settings = db_service.get_tenant_settings()
    
    assert settings == {"key": "db_val"}
    mock_cursor_context.execute.assert_called_once()
    assert db_service.settings_cache.get("tenant_settings") == {"key": "db_val"}

def test_get_system_prompt(mock_cursor_context):
    prompt_name = "sales_agent"
    db_service.settings_cache.invalidate(f"prompt_{prompt_name}")
    mock_cursor_context.fetchone.return_value = {"prompt_text": "Hello I am AI"}
    
    prompt = db_service.get_system_prompt(prompt_name)
    
    assert prompt == "Hello I am AI"
    mock_cursor_context.execute.assert_called_with(
        "SELECT prompt_text FROM system_prompts WHERE prompt_name = %s AND is_active = true",
        (prompt_name,)
    )

def test_get_all_offerings(mock_cursor_context):
    db_service.settings_cache.invalidate("off_None_True")
    mock_offerings = [{'name': 'Product A', 'price': 100}]
    mock_cursor_context.fetchall.return_value = mock_offerings
    
    offerings = db_service.get_all_offerings()
    
    assert offerings == mock_offerings
    assert "SELECT * FROM business_offerings" in mock_cursor_context.execute.call_args[0][0]

def test_create_offering(mock_cursor_context):
    mock_cursor_context.fetchone.return_value = {'id': 'off-123'}
    data = {'name': 'New Product', 'price': 50}
    
    off_id = db_service.create_offering(data)
    
    assert off_id == 'off-123'
    assert "INSERT INTO business_offerings" in mock_cursor_context.execute.call_args[0][0]

def test_update_offering(mock_cursor_context):
    success = db_service.update_offering('off-123', {'price': 60})
    
    assert success is True
    assert "UPDATE business_offerings" in mock_cursor_context.execute.call_args[0][0]

def test_save_message(mock_cursor_context):
    db_service.save_message("conv-1", "cust-1", "user", "Hello")
    
    # Check INSERT message
    assert "INSERT INTO messages" in mock_cursor_context.execute.call_args_list[0][0][0]
    # Check UPDATE customer profile
    assert "UPDATE customer_profiles" in mock_cursor_context.execute.call_args_list[1][0][0]

def test_get_conversation_history(mock_cursor_context):
    mock_rows = [
        {'sender_type': 'user', 'content': 'Hi'},
        {'sender_type': 'assistant', 'content': 'Hello there'}
    ]
    mock_cursor_context.fetchall.return_value = mock_rows
    
    history = db_service.get_conversation_history("conv-1")
    
    assert "العميل: Hi" in history
    assert "ياسمين: Hello there" in history

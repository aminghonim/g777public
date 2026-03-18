import pytest
from unittest.mock import patch, MagicMock

# Import modules so patch can resolve them
import backend.services.resend_client
import backend.services.cache_manager
import backend.services.pinecone_manager


# 1. Test Resend Client
@patch("backend.services.resend_client.resend.Emails.send")
def test_resend_email_success(mock_send):
    from backend.services.resend_client import resend_client
    
    # Mocking successful response
    mock_send.return_value = {"id": "re_123456789"}
    
    # Fake API key for testing
    resend_client.default_sender = "test@resend.dev"
    import resend
    resend.api_key = "test_key"
    
    response = resend_client.send_email(
        to_email="user@example.com",
        subject="Test Subject",
        html_content="<p>Hello World</p>"
    )
    
    assert response["status"] == "success"
    mock_send.assert_called_once()

# 2. Test Upstash Redis Rate Limiting
@patch("backend.services.cache_manager.Redis")
def test_rate_limiter_allows_under_limit(mock_redis):
    # Setup mock to return 1 (first request)
    mock_instance = MagicMock()
    mock_instance.incr.return_value = 1
    mock_redis.return_value = mock_instance
    
    from backend.services.cache_manager import CacheManager
    cm = CacheManager()
    cm.client = mock_instance # Force mocked client
    
    allowed = cm.check_rate_limit(identifier="user_123", limit=5, window_seconds=60)
    
    assert allowed is True
    mock_instance.incr.assert_called_with("rate_limit:user_123")
    mock_instance.expire.assert_called_with("rate_limit:user_123", 60)

@patch("backend.services.cache_manager.Redis")
def test_rate_limiter_blocks_over_limit(mock_redis):
    # Setup mock to return 6 (exceeded limit of 5)
    mock_instance = MagicMock()
    mock_instance.incr.return_value = 6
    mock_redis.return_value = mock_instance
    
    from backend.services.cache_manager import CacheManager
    cm = CacheManager()
    cm.client = mock_instance # Force mocked client
    
    allowed = cm.check_rate_limit(identifier="user_123", limit=5, window_seconds=60)
    
    assert allowed is False # Blocked!

# 3. Test Pinecone Tenant Isolation
@patch("backend.services.pinecone_manager.Pinecone")
def test_pinecone_upsert_enforces_tenant_id(mock_pc):
    mock_index = MagicMock()
    
    # Needs to be imported inside test to mock properly
    from backend.services.pinecone_manager import PineconeManager
    pm = PineconeManager()
    pm.index = mock_index
    
    vectors_to_insert = [
        {"id": "vec1", "values": [0.1, 0.2, 0.3], "metadata": {"source": "pdf"}},
        {"id": "vec2", "values": [0.4, 0.5, 0.6]} # No metadata originally
    ]
    
    pm.upsert_vectors(tenant_id="tenant_XYZ", vectors=vectors_to_insert)
    
    # Extract arguments passed to index.upsert
    called_args = mock_index.upsert.call_args[1]["vectors"]
    
    # Assert that ALL vectors got injected with the tenant_id binding
    for vec in called_args:
        assert "tenant_id" in vec["metadata"]
        assert vec["metadata"]["tenant_id"] == "tenant_XYZ"

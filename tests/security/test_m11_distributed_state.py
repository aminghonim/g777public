import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.security import SecurityEngine
from backend.services.cache_manager import CacheManager
from backend.routers.license import _check_guest_rate_limit

# ---------------------------------------------------------------------------
# M11 & M12: Distributed Token Blocklist & Rate Limiting Tests (GREEN PHASE)
# ---------------------------------------------------------------------------

def test_token_blocklist_uses_redis_with_memory_fallback():
    """
    Proves that SecurityEngine._token_blocklist uses Redis for distributed state.
    """
    jti = "test-jti-1234"
    
    # Ensure it's not in memory
    if jti in SecurityEngine._token_blocklist:
        SecurityEngine._token_blocklist.remove(jti)
        
    with patch.object(CacheManager, 'set') as mock_redis_set:
        SecurityEngine.revoke_token(jti)
        
        # In GREEN phase, it uses Redis
        mock_redis_set.assert_called_once()
        
        # It also keeps local memory as fallback
        assert jti in SecurityEngine._token_blocklist


def test_guest_rate_limit_uses_redis():
    """
    Proves that _check_guest_rate_limit uses Redis instead of local dict.
    """
    client_ip = "192.168.1.100"
    
    with patch.object(CacheManager, 'check_rate_limit', return_value=True) as mock_redis_ratelimit:
        # Call it once
        is_allowed = _check_guest_rate_limit(client_ip)
        
        assert is_allowed is True
        
        # Test must assert Redis was used
        mock_redis_ratelimit.assert_called_once_with(
            identifier=f"guest_token:{client_ip}",
            limit=5,
            window_seconds=60
        )

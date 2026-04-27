
import sys
import os
import subprocess
import pytest
from unittest.mock import patch, MagicMock
from jose import jwt

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.core.auth import ClerkAuth
from backend.core.rtk_enforcement import enforce_rtk_guard

class MockCredentials:
    def __init__(self, token):
        self.credentials = token

@pytest.mark.asyncio
async def test_jwt_aud_verification_bypass():
    """
    Test that JWT audience verification can currently be bypassed (should fail after fix).
    We mock a JWT that has an incorrect 'aud', but because 'verify_aud' is False, 
    it should still pass in the CURRENT state.
    """
    mock_token = "mock.payload.secret"
    mock_jwks = {"keys": []}
    
    # We mock jwt.decode to simulate what happens when verify_aud=False
    # In the real code, it doesn't check the audience, so it returns payload.
    with patch("backend.core.auth._get_jwks", return_value=mock_jwks):
        with patch("jose.jwt.decode", return_value={"sub": "user_123", "aud": "wrong_aud"}) as mock_decode:
            creds = MockCredentials(mock_token)
            result = await ClerkAuth.verify_token(creds)
            
            assert result["user_id"] == "user_123"
            # In the CURRENT state, this passes even with wrong_aud. 
            # In the FIXED state, jose.jwt.decode should be called with verify_aud=True/audience check.

def test_rtk_enforcement_vulnerability():
    """
    Test if we can bypass RTK enforcement by wrapping the call to increase stack depth.
    Current enforcement uses sys._getframe(3).
    """
    # 0: sys._getframe
    # 1: enforce_rtk_guard
    # 2: patched_subprocess
    # 3: CALLER (whitelisted or not)
    
    # Let's see if we can trick it by adding one more layer
    def malicious_wrapper(*args, **kwargs):
        return subprocess.run(*args, **kwargs) # This will call the patched version

    def deep_wrapper(*args, **kwargs):
        return malicious_wrapper(*args, **kwargs)

    # Current RTK enforcement:
    # 0: _getframe
    # 1: enforce_rtk_guard
    # 2: run (patched)
    # 3: deep_wrapper (Unknown caller -> Blocked)
    
    # However, if someone calls it from a whitelisted module but at a DIFFERENT depth,
    # it might bypass or block incorrectly. 
    # This test is more about demonstrating the fragility of hardcoded frame offsets.
    pass

def test_sqlite_in_production_guard():
    """
    Verify that SQLite is blocked if DATABASE_URL is used in a production context.
    """
    # This will be implemented in DatabaseManager.__init__
    pass

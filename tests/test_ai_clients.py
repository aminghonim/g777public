
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from backend.ai_client import GeminiAIClient, UnifiedAIClient

class TestAIClients:
    @pytest.mark.asyncio
    async def test_gemini_client_flow(self):
        """تغطية GeminiAIClient"""
        with patch('google.genai.Client') as mock_client:
            client = GeminiAIClient(api_key="test")
            mock_client.return_value.aio.models.generate_content = AsyncMock()
            mock_client.return_value.aio.models.generate_content.return_value.text = "Hello"
            
            resp = await client.generate_response("Hi")
            assert resp == "Hello"

@pytest.mark.asyncio
async def test_ai_service_direct_call():
    """تغطية call_gemini_direct في ai_service.py"""
    with patch('backend.ai_client.GeminiAIClient') as mock_cls:
        mock_cls.return_value.generate_response = AsyncMock(return_value="Direct")
        resp = await call_gemini_direct("Test message")
        assert resp == "Direct"

def test_unified_client_routing():
    """تغطية UnifiedAIClient"""
    with patch('backend.ai_client.GeminiAIClient'):
        client = UnifiedAIClient(provider="gemini", api_key="test")
        assert client.primary == "gemini"

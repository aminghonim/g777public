
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create global mocks for providers
mock_genai_module = MagicMock()
mock_anthropic_module = MagicMock()

@pytest.fixture(autouse=True)
def mock_external_modules():
    """Ensure external modules are always mocked during these tests"""
    with patch.dict(sys.modules, {
        "google": mock_genai_module,
        "google.genai": mock_genai_module.genai,
        "anthropic": mock_anthropic_module
    }):
        yield

# Import clients AFTER starting global mocks
from backend.ai_client import GeminiAIClient, ClaudeAIClient, UnifiedAIClient

class TestAIClientSurgical:
    """
    Surgical Coverage Test for backend/ai_client.py (Gemini & Claude)
    """

    @pytest.fixture
    def gemini_mock(self):
        with patch('backend.ai_client.genai.Client') as mock_client:
            yield mock_client

    def test_gemini_init_success(self, gemini_mock):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
            with patch('backend.ai_client.logger') as mock_logger:
                client = GeminiAIClient()
                assert client.api_key == "test_key"
                assert client.client is not None
                gemini_mock.assert_called_with(api_key="test_key")
                mock_logger.info.assert_called()

    def test_gemini_init_no_key(self, gemini_mock):
        with patch.dict(os.environ, {}, clear=True):
            client = GeminiAIClient(api_key=None)
            assert client.client is None

    @pytest.mark.asyncio
    async def test_gemini_generate_response(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Gemini Reply"
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        
        client = GeminiAIClient(api_key="key")
        client.client = mock_client
        
        res = await client.generate_response("Hi", "System")
        assert res == "Gemini Reply"

    def test_claude_init_success(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "claude_key"}):
            with patch('backend.ai_client.AsyncAnthropic') as mock_claude_class:
                client = ClaudeAIClient()
                assert client.client is not None
                mock_claude_class.assert_called_with(api_key="claude_key")

    @pytest.mark.asyncio
    async def test_claude_generate_response_success(self):
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.content = [MagicMock()]
        mock_resp.content[0].text = "Claude Reply"
        mock_client.messages.create.return_value = mock_resp
        
        client = ClaudeAIClient(api_key="key")
        client.client = mock_client
        
        res = await client.generate_response("Hi")
        assert res == "Claude Reply"

    def test_unified_init_gemini(self):
        with patch('backend.ai_client.GeminiAIClient') as mock_g:
            client = UnifiedAIClient(provider="gemini", api_key="k")
            assert client.primary == "gemini"

    def test_unified_init_claude(self):
        with patch('backend.ai_client.ClaudeAIClient') as mock_c:
            mock_c.return_value.client = MagicMock()
            client = UnifiedAIClient(provider="claude")
            assert client.primary == "claude"

    def test_unified_init_auto_fallback(self):
        # Case: Gemini init works
        with patch('backend.ai_client.GeminiAIClient') as mock_g:
            client = UnifiedAIClient()
            assert client.primary == "gemini"
            
        # Case: Gemini fails, Claude succeeds
        with patch('backend.ai_client.GeminiAIClient', side_effect=Exception("Fail")), \
             patch('backend.ai_client.ClaudeAIClient') as mock_c:
            mock_c.return_value.client = MagicMock()
            client = UnifiedAIClient()
            assert client.primary == "claude"

    @pytest.mark.asyncio
    async def test_unified_generate_response_flows(self):
        with patch('backend.ai_client.GeminiAIClient') as mock_g_class, \
             patch('backend.ai_client.ClaudeAIClient') as mock_c_class:
            
            mock_g_inst = mock_g_class.return_value
            mock_c_inst = mock_c_class.return_value
            mock_c_inst.client = MagicMock()
            
            client = UnifiedAIClient()
            client.gemini_client = mock_g_inst
            client.claude_client = mock_c_inst
            
            # Case 1: Primary Gemini Success
            client.primary = "gemini"
            mock_g_inst.generate_response = AsyncMock(return_value="G ok")
            assert await client.generate_response("H") == "G ok"
            
            # Case 2: Primary Gemini Fail -> Fallback Claude
            mock_g_inst.generate_response.side_effect = Exception("G dead")
            mock_c_inst.generate_response = AsyncMock(return_value="C fallback")
            assert await client.generate_response("H") == "C fallback"
            
            # Case 3: Both Fail
            mock_c_inst.generate_response.side_effect = Exception("C dead")
            assert "All AI providers failed" in await client.generate_response("H")

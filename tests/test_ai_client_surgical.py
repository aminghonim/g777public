
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create global mocks for providers
mock_genai_module = MagicMock()
mock_openai_module = MagicMock()

@pytest.fixture(autouse=True)
def mock_external_modules():
    """Ensure external modules are always mocked during these tests"""
    with patch.dict(sys.modules, {
        "google": mock_genai_module,
        "google.genai": mock_genai_module.genai,
        "openai": mock_openai_module
    }):
        yield

# Import clients AFTER starting global mocks if possible, 
# but here we'll use patch.object or patch in individual tests to be safe.
from backend.ai_client import GeminiAIClient, AzureAIClient, UnifiedAIClient

class TestAIClientSurgical:
    """
    Surgical Coverage Test for backend/ai_client.py
    """

    @pytest.fixture
    def gemini_mock(self):
        with patch('google.genai.Client') as mock_client:
            yield mock_client

    def test_gemini_init_success(self, gemini_mock):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
            client = GeminiAIClient()
            assert client.api_key == "test_key"
            assert client.client is not None
            gemini_mock.assert_called_with(api_key="test_key")

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

    def test_gemini_generate_response_sync(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Sync Reply"
        mock_client.models.generate_content.return_value = mock_response
        
        client = GeminiAIClient(api_key="key")
        client.client = mock_client
        
        res = client.generate_response_sync("Hi", "System")
        assert res == "Sync Reply"

    def test_azure_init_success(self):
        with patch.dict(os.environ, {
            "AZURE_OPENAI_API_KEY": "azure_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.azure.com"
        }):
            # Mock the class inside the openai module
            mock_azure_class = MagicMock()
            mock_openai_module.AsyncAzureOpenAI = mock_azure_class
            
            client = AzureAIClient()
            assert client.client is not None
            mock_azure_class.assert_called()

    def test_azure_init_missing_creds(self):
        with patch.dict(os.environ, {}, clear=True):
            client = AzureAIClient()
            assert client.client is None

    @pytest.mark.asyncio
    async def test_azure_generate_response_success(self):
        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock()]
        mock_resp.choices[0].message.content = "Azure Reply"
        mock_client.chat.completions.create.return_value = mock_resp
        
        client = AzureAIClient()
        client.client = mock_client
        
        res = await client.generate_response("Hi")
        assert res == "Azure Reply"

    @pytest.mark.asyncio
    async def test_azure_generate_response_fail(self):
        client = AzureAIClient()
        client.client = None
        res = await client.generate_response("Hi")
        assert "not configured" in res

        client._primary = "azure" # Not needed but good for clarity
        client.client = AsyncMock()
        client.client.chat.completions.create.side_effect = Exception("Azure Down")
        res = await client.generate_response("Hi")
        assert "Error: Azure Down" in res

    def test_unified_init_gemini(self):
        # We need to patch BOTH the class and where it's used if they are in the same module
        with patch('backend.ai_client.GeminiAIClient') as mock_g:
            client = UnifiedAIClient(provider="gemini", api_key="k")
            assert client.primary == "gemini"

    def test_unified_init_azure(self):
        with patch('backend.ai_client.AzureAIClient') as mock_a:
            mock_a.return_value.client = MagicMock()
            client = UnifiedAIClient(provider="azure")
            assert client.primary == "azure"

    def test_unified_init_auto_fallback(self):
        # Case: Gemini init works
        with patch('backend.ai_client.GeminiAIClient') as mock_g:
            client = UnifiedAIClient()
            assert client.primary == "gemini"
            
        # Case: Gemini fails, Azure succeeds
        with patch('backend.ai_client.GeminiAIClient', side_effect=Exception("Fail")), \
             patch('backend.ai_client.AzureAIClient') as mock_a:
            mock_a.return_value.client = MagicMock()
            client = UnifiedAIClient()
            assert client.primary == "azure"

    def test_unified_init_force_exceptions(self):
        # Force exception in Gemini init (line 113)
        with patch('backend.ai_client.GeminiAIClient', side_effect=Exception("Boom")):
            client = UnifiedAIClient(provider="gemini")
            assert client.gemini_client is None
            
        # Force exception in Azure init (line 121)
        with patch('backend.ai_client.AzureAIClient', side_effect=Exception("Boom")):
            client = UnifiedAIClient(provider="azure")
            assert client.azure_client is None

    def test_azure_import_error(self):
        # Mock sys.modules to simulate missing openai (line 77-78)
        # MUST provide env vars so it moves past line 66
        with patch.dict(os.environ, {
            "AZURE_OPENAI_API_KEY": "real_key",
            "AZURE_OPENAI_ENDPOINT": "https://real.endpoint"
        }):
            with patch.dict('sys.modules', {'openai': None}):
                with patch('builtins.print') as mock_print:
                    # In some environments, once imported it stays. 
                    # But AzureAIClient does 'from openai import ...' INSIDE __init__ if not at top.
                    # Wait, is it at top? No, it's inside line 70.
                    client = AzureAIClient()
                    assert client.client is None
                    mock_print.assert_any_call("[WARN] openai package not installed")



    @pytest.mark.asyncio
    async def test_unified_generate_response_flows(self):
        # We need to mock the internal clients
        with patch('backend.ai_client.GeminiAIClient') as mock_g_class, \
             patch('backend.ai_client.AzureAIClient') as mock_a_class:
            
            mock_g_inst = mock_g_class.return_value
            mock_a_inst = mock_a_class.return_value
            mock_a_inst.client = MagicMock() # Azure needs 'client' attr to be considered active
            
            client = UnifiedAIClient()
            client.gemini_client = mock_g_inst
            client.azure_client = mock_a_inst
            
            # Case 1: Primary Gemini Success
            client.primary = "gemini"
            mock_g_inst.generate_response = AsyncMock(return_value="G ok")
            assert await client.generate_response("H") == "G ok"
            
            # Case 2: Primary Gemini Fail -> Fallback Azure
            mock_g_inst.generate_response.side_effect = Exception("G dead")
            mock_a_inst.generate_response = AsyncMock(return_value="A fallback")
            assert await client.generate_response("H") == "A fallback"
            
            # Case 3: Both Fail
            mock_a_inst.generate_response.side_effect = Exception("A dead")
            assert "All AI providers failed" in await client.generate_response("H")

            # Case 4: Primary is Azure (line 150-151)
            client.primary = "azure"
            mock_a_inst.generate_response = AsyncMock(return_value="A direct")
            assert await client.generate_response("H") == "A direct"


    def test_unified_init_all_fail(self):
        with patch('backend.ai_client.GeminiAIClient', side_effect=Exception), \
             patch('backend.ai_client.AzureAIClient', side_effect=Exception):
            client = UnifiedAIClient()
            assert client.primary is None


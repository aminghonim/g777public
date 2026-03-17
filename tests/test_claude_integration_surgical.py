import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from backend.ai_client import ClaudeAIClient, UnifiedAIClient

class TestClaudeIntegrationSurgical:
    """
    Surgical unit tests for Claude integration (Anthropic).
    Adheres to Rule 4 (Zero-Regression) and Rule 8 (Coding Standards).
    """

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""})
    def test_claude_init_missing_key(self):
        """Test Claude client initialization without API key (Failure Case)"""
        with patch("backend.ai_client.logger") as mock_logger:
            client = ClaudeAIClient()
            assert client.client is None
            mock_logger.warning.assert_called_with("ANTHROPIC_API_KEY not set. Claude client disabled.")

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"})
    @patch("backend.ai_client.AsyncAnthropic")
    def test_claude_init_success(self, mock_anthropic):
        """Test successful Claude client initialization"""
        client = ClaudeAIClient()
        assert client.client is not None
        mock_anthropic.assert_called_once_with(api_key="test_key")

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"})
    async def test_claude_generate_response_success(self):
        """Test Claude response generation success"""
        with patch("backend.ai_client.AsyncAnthropic") as mock_async_anthropic:
            mock_instance = mock_async_anthropic.return_value
            # Claude client in the code is created with AsyncAnthropic(api_key=...)
            # And it uses client.messages.create
            mock_instance.messages.create = AsyncMock()
            
            # Mock the response structure: resp.content[0].text
            mock_resp = MagicMock()
            mock_content = MagicMock()
            mock_content.text = "Hello from Claude"
            mock_resp.content = [mock_content]
            mock_instance.messages.create.return_value = mock_resp

            client = ClaudeAIClient()
            # The client.client will be the mock instance because of the patch
            
            response = await client.generate_response("Hi Claude")
            assert response == "Hello from Claude"
            mock_instance.messages.create.assert_called_once()

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"})
    async def test_claude_generate_response_error(self):
        """Test Claude response generation error handling"""
        with patch("backend.ai_client.AsyncAnthropic") as mock_async_anthropic:
            mock_instance = mock_async_anthropic.return_value
            mock_instance.messages.create = AsyncMock(side_effect=Exception("Anthropic limit"))
            
            client = ClaudeAIClient()
            response = await client.generate_response("Hi Claude")
            assert "Error: Anthropic limit" in response

    @patch.dict(os.environ, {
        "GEMINI_API_KEY": "",
        "ANTHROPIC_API_KEY": "claude_key",
        "AZURE_OPENAI_API_KEY": ""
    })
    @patch("backend.ai_client.ClaudeAIClient")
    def test_unified_fallback_to_claude(self, mock_claude_class):
        """Test UnifiedAIClient falling back to Claude when Gemini is missing"""
        # Mock Claude client instance
        mock_claude_inst = MagicMock()
        mock_claude_inst.client = MagicMock()
        mock_claude_class.return_value = mock_claude_inst
        
        with patch("backend.ai_client.GeminiAIClient") as mock_gemini_class:
            # Force Gemini to be empty/inactive
            mock_gemini_inst = MagicMock()
            mock_gemini_inst.client = None
            mock_gemini_class.return_value = mock_gemini_inst
            
            client = UnifiedAIClient()
            assert client.primary == "claude"
            assert client.claude_client is not None

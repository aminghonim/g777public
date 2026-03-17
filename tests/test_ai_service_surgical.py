
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from backend.ai_service import call_gemini_direct

class TestAIServiceSurgical:

    @pytest.mark.asyncio
    async def test_call_gemini_direct_success(self):
        """اختبار الاستدعاء المباشر بنجاح"""
        with patch('backend.ai_client.GeminiAIClient.generate_response', AsyncMock(return_value="Gemini Output")):
            res = await call_gemini_direct("Hello")
            assert res == "Gemini Output"

    @pytest.mark.asyncio
    async def test_call_gemini_direct_exception(self):
        """تغطية الـ except في حالة فشل الاستدعاء"""
        with patch('backend.ai_client.GeminiAIClient.generate_response', side_effect=Exception("API Error")):
            res = await call_gemini_direct("Hello")
            assert res is None

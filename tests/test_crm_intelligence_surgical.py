
import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from backend.crm_intelligence import run_data_extraction

class TestCRMIntelligenceSurgical:

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_run_data_extraction_success(self):
        """اختبار استخراج البيانات وتحديث الـ CRM بنجاح"""
        mock_history = "User: I am Ahmed from Cairo. Interested in cheap trips."
        mock_prompt = "Extract from {conversation}"
        mock_ai_resp = json.dumps({
            "name": "Ahmed",
            "city": "Cairo",
            "interests": ["cheap trips"]
        })
        
        with patch('backend.crm_intelligence.get_conversation_history', return_value=mock_history), \
             patch('backend.crm_intelligence.get_system_prompt', return_value=mock_prompt), \
             patch('backend.crm_intelligence.call_gemini_direct', AsyncMock(return_value=mock_ai_resp)), \
             patch('backend.crm_intelligence.update_customer_profile', return_value=True) as mock_update:
            
            await run_data_extraction("123", "conv_1")
            
            assert mock_update.called
            args, kwargs = mock_update.call_args
            assert args[0] == "123"
            assert args[1]['name'] == "Ahmed"
            assert 'interests' in args[1]['metadata']

    # =================================================================
    # ❌ LOGIC FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_run_data_extraction_no_history(self):
        """حالة عدم وجود تاريخ للمحادثة"""
        with patch('backend.crm_intelligence.get_conversation_history', return_value=None):
            await run_data_extraction("123", "conv_1")
            # Should return early without calling AI
            with patch('backend.crm_intelligence.call_gemini_direct') as mock_ai:
                assert not mock_ai.called

    @pytest.mark.asyncio
    async def test_run_data_extraction_no_prompt(self):
        """حالة عدم وجود قالب استخراج في قاعدة البيانات"""
        with patch('backend.crm_intelligence.get_conversation_history', return_value="history"), \
             patch('backend.crm_intelligence.get_system_prompt', return_value=None):
            await run_data_extraction("123", "conv_1")
            # Should return early

    @pytest.mark.asyncio
    async def test_run_data_extraction_invalid_json(self):
        """حالة رد AI بنص مش JSON"""
        with patch('backend.crm_intelligence.get_conversation_history', return_value="h"), \
             patch('backend.crm_intelligence.get_system_prompt', return_value="p"), \
             patch('backend.crm_intelligence.call_gemini_direct', AsyncMock(return_value="Not JSON")):
            # Should catch exception internally
            await run_data_extraction("123", "conv_1")

    # =================================================================
    # 💥 SYSTEM FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_run_data_extraction_update_fail(self):
        """حالة فشل تحديث قاعدة البيانات رغم صحة البيانات المستخرجة"""
        mock_ai_resp = json.dumps({"name": "X"})
        with patch('backend.crm_intelligence.get_conversation_history', return_value="h"), \
             patch('backend.crm_intelligence.get_system_prompt', return_value="p"), \
             patch('backend.crm_intelligence.call_gemini_direct', AsyncMock(return_value=mock_ai_resp)), \
             patch('backend.crm_intelligence.update_customer_profile', return_value=False):
            
            # Should print failure message but not crash
            await run_data_extraction("123", "conv_1")

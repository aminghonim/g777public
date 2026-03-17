
import pytest
from backend.ai_engine import AIEngine
from unittest.mock import AsyncMock, patch
import json
import asyncio

@pytest.mark.asyncio
async def test_ai_engine_full_cycle():
    """اختبار دورة الذكاء الاصطناعي الكاملة لمخ ياسمين"""
    engine = AIEngine()
    
    # 1. اختبار تحليل النية (Intent Analysis)
    with patch.object(engine.client.aio.models, 'generate_content', new_callable=AsyncMock) as mock_gen:
        # محاكاة رد الذكاء الاصطناعي كـ JSON للنوايا
        mock_gen.return_value.text = '{"intent": "price_inquiry", "sentiment": "positive"}'
        
        intent_data = await engine.analyze_intent("بكام الرحلة؟")
        assert intent_data['intent'] == "price_inquiry"

    # 2. اختبار استخراج البيانات (Data Extraction) - now async
    customer_mock = {"phone": "201000000000", "missing_fields": ["name", "location"]}
    with patch.object(engine.client.aio.models, 'generate_content', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value.text = '{"name": "Ahmed", "location": "Cairo"}'
        
        # Mock DB functions at source (db_service) to isolate from real database
        with patch('backend.db_service.mark_field_collected'), \
             patch('backend.db_service.update_customer'):
            # extract_and_update_info is now async - must await it
            extracted = await engine.extract_and_update_info("انا احمد من القاهرة", customer_mock)
            assert extracted['name'] == "Ahmed"

    # 3. اختبار توليد الرد (Response Generation)
    with patch.object(engine.client.aio.models, 'generate_content', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value.text = "سعر الرحلة 450 جنيه يا فندم"
        
        response = await engine.generate_response("201000000000", "بكام؟", "User: Hi")
        assert "450" in response

def test_ai_engine_load_instructions():
    """التأكد من أن المحرك يقرأ التعليمات من ملف YAML"""
    engine = AIEngine()
    instructions = engine._load_instructions()
    assert instructions is not None
    # Updated assertion to match new config structure
    assert "main_assistant" in instructions or "identity" in instructions or "direct_sales" in str(instructions).lower()

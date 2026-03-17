
import pytest
from unittest.mock import AsyncMock, patch
from backend.ai_engine import AIEngine

@pytest.fixture
def engine():
    return AIEngine()

@pytest.mark.asyncio
async def test_ai_intent_analysis(engine):
    """اختبار تحليل النوايا"""
    with patch.object(engine.client.aio.models, 'generate_content', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value.text = '{"intent": "sales", "sentiment": "positive"}'
        result = await engine.analyze_intent("بكام الرحلة؟")
        assert result['intent'] == "sales"

@pytest.mark.asyncio
async def test_ai_response_generation(engine):
    """اختبار توليد الردود"""
    with patch.object(engine.client.aio.models, 'generate_content', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value.text = "السعر 450 جنيه"
        response = await engine.generate_response("201000000000", "بكام؟")
        assert "450" in response

def test_ai_load_config(engine):
    """اختبار تحميل الإعدادات"""
    instructions = engine._load_instructions()
    assert instructions is not None

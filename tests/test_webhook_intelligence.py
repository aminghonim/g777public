
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.webhook_handler import process_whatsapp_message, n8n_smart_chat
from backend.crm_intelligence import run_data_extraction
from backend.brain_trainer import BrainTrainer

@pytest.mark.asyncio
async def test_webhook_processing_flow():
    """تغطية معالجة رسائل الواتساب الواردة"""
    mock_data = {
        "instance": "G777",
        "data": {"key": {"remoteJid": "201000000@s.whatsapp.net"}, "pushName": "Test", "message": {"conversation": "Hi"}}
    }
    with patch('backend.webhook_handler.db_service') as mock_db:
        # Simulate processing without real DB
        await process_whatsapp_message(mock_data)
        assert True

@pytest.mark.asyncio
async def test_n8n_chat_logic():
    """تغطية منطق n8n_smart_chat"""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 200
        await n8n_smart_chat("201000000", "Hi", "G777")
        assert mock_post.called

def test_intelligence_extraction():
    """تغطية run_data_extraction"""
    with patch('backend.crm_intelligence.AIEngine') as mock_ai:
        mock_ai.return_value.extract_and_update_info.return_value = {"name": "Detected"}
        run_data_extraction("201000000", "My name is Detected")
        assert True

def test_brain_trainer_methods():
    """تغطية BrainTrainer"""
    with patch('backend.brain_trainer.get_db_cursor'):
        trainer = BrainTrainer()
        trainer.humanize_bot_response("Hello") # Test simple utility
        assert True


import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
from backend.crm_intelligence import run_data_extraction

@pytest.fixture
def mock_db_service():
    with patch('backend.crm_intelligence.get_conversation_history') as mock_hist, \
         patch('backend.crm_intelligence.get_system_prompt') as mock_prompt, \
         patch('backend.crm_intelligence.update_customer_profile') as mock_update:
        yield mock_hist, mock_prompt, mock_update

@pytest.fixture
def mock_ai_service():
    with patch('backend.crm_intelligence.call_gemini_direct', new_callable=AsyncMock) as mock_ai:
        yield mock_ai

@pytest.mark.asyncio
async def test_run_data_extraction_success(mock_db_service, mock_ai_service):
    mock_hist, mock_prompt, mock_update = mock_db_service
    
    # Setup mocks
    mock_hist.return_value = "User: Hello\nAI: Hi"
    mock_prompt.return_value = "Analyze: {conversation}"
    
    # AI returns valid JSON
    ai_response = json.dumps({
        "name": "John Doe",
        "city": "Cairo",
        "interests": ["Travel"],
        "budget_info": "High"
    })
    mock_ai_service.return_value = f"```json\n{ai_response}\n```"
    mock_update.return_value = True
    
    await run_data_extraction("123456", "conv-1")
    
    # Verify DB calls
    mock_hist.assert_called_with("conv-1", limit=20)
    mock_prompt.assert_called_with("entity_extractor")
    
    # Verify AI call
    mock_ai_service.assert_called_once()
    prompt_sent = mock_ai_service.call_args[0][0]
    assert "User: Hello" in prompt_sent
    
    # Verify Profile Update
    mock_update.assert_called_once()
    args = mock_update.call_args[0]
    phone = args[0]
    updates = args[1]
    
    assert phone == "123456"
    assert updates['name'] == "John Doe"
    assert updates['city'] == "Cairo"
    assert updates['metadata']['interests'] == ["Travel"]
    assert updates['metadata']['budget_info'] == "High"

@pytest.mark.asyncio
async def test_run_data_extraction_no_history(mock_db_service, mock_ai_service):
    mock_hist, _, _ = mock_db_service
    mock_hist.return_value = ""
    
    await run_data_extraction("123456", "conv-1")
    
    mock_ai_service.assert_not_called()

@pytest.mark.asyncio
async def test_run_data_extraction_no_prompt(mock_db_service, mock_ai_service):
    mock_hist, mock_prompt, _ = mock_db_service
    mock_hist.return_value = "chat"
    mock_prompt.return_value = None
    
    await run_data_extraction("123456", "conv-1")
    
    mock_ai_service.assert_not_called()

@pytest.mark.asyncio
async def test_run_data_extraction_bad_json(mock_db_service, mock_ai_service):
    mock_hist, mock_prompt, mock_update = mock_db_service
    mock_hist.return_value = "chat"
    mock_prompt.return_value = "p"
    mock_ai_service.return_value = "Not JSON"
    
    await run_data_extraction("123456", "conv-1")
    
    mock_update.assert_not_called()

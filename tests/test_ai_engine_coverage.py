import pytest
from unittest.mock import MagicMock, AsyncMock, patch, mock_open
import sys
import os
import json

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_engine import AIEngine, ai_engine


class TestAIEngineCoverage:
    """
    Surgical Coverage Test for backend/ai_engine.py
    Target: Increase coverage from 0% to nearly 100%
    """

    @pytest.fixture(autouse=True)
    def mock_genai_client(self):
        """Mock the google.genai.Client and VectorStoreManager"""
        with patch("google.genai.Client") as MockClient, patch(
            "backend.agents.orchestrator.VectorStoreManager"
        ) as MockVector:

            mock_instance = MockClient.return_value
            mock_instance.aio.models.generate_content = AsyncMock()

            # Ensure recall_memory returns empty by default
            MockVector.return_value.search_memory.return_value = {
                "ids": [[]],
                "documents": [[]],
            }

            yield mock_instance

    @pytest.fixture
    def mock_db_service(self):
        """Mock all db_service functions used"""
        with patch("backend.ai_engine.get_tenant_settings") as mock_settings, patch(
            "backend.ai_engine.get_system_prompt"
        ) as mock_prompt, patch(
            "backend.ai_engine.get_customer_by_phone"
        ) as mock_cust, patch(
            "backend.ai_engine.is_excluded"
        ) as mock_excluded, patch(
            "backend.ai_engine.get_training_samples"
        ) as mock_training, patch(
            "backend.ai_engine.format_offerings_for_prompt"
        ) as mock_offerings:

            mock_settings.return_value = {
                "ai_model": "gemini-2.0-flash",
                "business_name": "TestBiz",
            }
            mock_prompt.return_value = "System says {business_name}"
            mock_cust.return_value = {
                "phone": "123",
                "name": "Test User",
                "missing_fields": ["name"],
            }
            mock_excluded.return_value = False
            mock_training.return_value = ""
            mock_offerings.return_value = "Offer A - 100$"

            yield {
                "settings": mock_settings,
                "prompt": mock_prompt,
                "cust": mock_cust,
                "excluded": mock_excluded,
                "training": mock_training,
                "offerings": mock_offerings,
            }

    def test_init_loading(self):
        """Test initialization and instructions loading"""
        # Test 1: Config file exists
        mock_yaml = "intent_classifier: {role: 'Tester'}"
        real_open = open

        def open_side_effect(filename, *args, **kwargs):
            if "strings.json" in str(filename):
                return mock_open(read_data="{}").return_value
            if "ai_instructions.yaml" in str(filename):
                return mock_open(read_data=mock_yaml).return_value
            return real_open(filename, *args, **kwargs)

        with patch("builtins.open", side_effect=open_side_effect):
            with patch(
                "yaml.safe_load", return_value={"intent_classifier": {"role": "Tester"}}
            ):
                engine = AIEngine()
                assert engine.instructions["intent_classifier"]["role"] == "Tester"

        # Test 2: Config file missing/error
        with patch("builtins.open", side_effect=FileNotFoundError):
            engine = AIEngine()
            assert engine.instructions == {}

    @pytest.mark.asyncio
    async def test_analyze_intent(self, mock_genai_client, mock_db_service):
        """Test analyze_intent logic"""
        engine = AIEngine()

        # Scenario 1: Successful Intent Analysis
        mock_response = MagicMock()
        mock_response.text = '```json\n{"is_business": true, "intent": "booking"}\n```'
        mock_genai_client.aio.models.generate_content.return_value = mock_response

        result = await engine.analyze_intent("I want to book")
        assert result["is_business"] is True
        assert result["intent"] == "booking"

        # Scenario 2: API Error
        mock_genai_client.aio.models.generate_content.side_effect = Exception(
            "API Down"
        )
        result = await engine.analyze_intent("Hello")
        assert result["intent"] == "unknown"
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_extract_info(self, mock_genai_client, mock_db_service):
        """Test extract_and_update_info logic"""
        engine = AIEngine()
        customer = {"phone": "123", "missing_fields": ["location"]}

        # Scenario 1: Extraction Success
        mock_response = MagicMock()
        mock_response.text = '{"location": "Cairo", "job": "Engineer"}'
        mock_genai_client.aio.models.generate_content.return_value = mock_response

        # We need to mock the update function imported inside (patch where it comes from)
        with patch("backend.db_service.update_customer") as mock_update:
            with patch("backend.db_service.mark_field_collected") as mock_mark:
                updated_cust = await engine.extract_and_update_info(
                    "I live in Cairo", customer
                )

                # 'location' is treated as top-level field in ai_engine.py
                assert updated_cust.get("location") == "Cairo"
                # 'job' should go to custom_data
                assert updated_cust.get("custom_data") == {"job": "Engineer"}
                mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_response_logic(self, mock_genai_client, mock_db_service):
        """Test generate_response logic flows"""
        engine = AIEngine()

        # Scenario 1: Excluded User
        mock_db_service["excluded"].return_value = True
        res = await engine.generate_response("Hi", "999")
        assert res == ""

        # Scenario 2: Normal Flow
        mock_db_service["excluded"].return_value = False
        mock_resp = MagicMock()
        mock_resp.text = "Hello Customer"
        mock_genai_client.aio.models.generate_content.return_value = mock_resp

        # Mocking trips_db.json read
        with patch(
            "builtins.open",
            mock_open(
                read_data='{"trips": [{"type": "DayUse", "price": 500, "includes": ["Lunch"]}]}'
            ),
        ):
            res = await engine.generate_response("Hi", "123")
            assert "Hello Customer" in res

            # Verify call contained offerings
            call_args = mock_genai_client.aio.models.generate_content.call_args
            sent_prompt = call_args.kwargs["contents"][0].parts[0].text
            assert "DayUse: 500" in sent_prompt

        # Scenario 3: Exception Handling (e.g., File Error + API Error)
        with patch("builtins.open", side_effect=IOError):
            mock_genai_client.aio.models.generate_content.side_effect = Exception(
                "Fail"
            )
            res = await engine.generate_response("Hi", "123")
            assert "System Error" in res or "خطأ" in res

    @pytest.mark.asyncio
    async def test_init_missing_key(self):
        """Cover Line 31: Warning when API Key is missing"""
        with patch("backend.ai_engine.os.getenv", return_value=None):
            with patch("backend.ai_engine.logger.error") as mock_log:
                # Re-init to trigger the check
                AIEngine()
                mock_log.assert_called()

    @pytest.mark.asyncio
    async def test_extract_info_no_missing_fields(
        self, mock_genai_client, mock_db_service
    ):
        """Cover Line 100: Early exit if no missing fields"""
        engine = AIEngine()
        customer = {"phone": "123", "missing_fields": []}  # Empty list

        updated_cust = await engine.extract_and_update_info("Msg", customer)
        assert updated_cust == customer
        # Ensure API was NOT called
        mock_genai_client.aio.models.generate_content.assert_not_called()

    @pytest.mark.asyncio
    async def test_training_mode_context(self, mock_genai_client, mock_db_service):
        """Cover Line 241: TRAINING_MODE context generation"""
        engine = AIEngine()

        # Mock successful generation to avoid error handling path
        mock_resp = MagicMock()
        mock_resp.text = "Training Reply"
        mock_genai_client.aio.models.generate_content.return_value = mock_resp

        # We need to verify full call arguments to ensure correct context was used
        with patch("builtins.open", mock_open(read_data='{"trips": []}')):
            await engine.generate_response(
                "Hi", "TRAINING_MODE", conversation_history="Old Chat"
            )

            call_args = mock_genai_client.aio.models.generate_content.call_args
            sent_prompt = call_args.kwargs["contents"][0].parts[0].text
            # Ensure training context logic was hit
            assert "Chat History" in sent_prompt

    @pytest.mark.asyncio
    async def test_summarize_customer(self, mock_genai_client, mock_db_service):
        """Test summarization"""
        engine = AIEngine()

        mock_resp = MagicMock()
        mock_resp.text = "Summary"
        mock_genai_client.aio.models.generate_content.return_value = mock_resp

        res = await engine.summarize_customer("Chat log")
        assert res == "Summary"

        # Error case
        mock_genai_client.aio.models.generate_content.side_effect = Exception()
        res = await engine.summarize_customer("Chat log")
        assert res == ""


if __name__ == "__main__":
    pytest.main([__file__])

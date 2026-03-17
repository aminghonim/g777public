import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.warmer import AccountWarmer


@pytest.mark.asyncio
async def test_generate_human_like_message_success():
    # Mock AI Client
    mock_ai = MagicMock()
    mock_ai.generate_response = AsyncMock(return_value="أهلاً بك يا صديقي")

    warmer = AccountWarmer(ai_client=mock_ai)

    # Run test
    message = await warmer.generate_human_like_message()

    # Assertions
    assert message == "أهلاً بك يا صديقي"
    mock_ai.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_generate_human_like_message_fallback():
    # Mock AI Client to throw error
    mock_ai = MagicMock()
    mock_ai.generate_response = AsyncMock(side_effect=Exception("AI Offline"))

    warmer = AccountWarmer(ai_client=mock_ai)

    # Run test
    message = await warmer.generate_human_like_message()

    # Assertions
    fallbacks = [
        "أهلاً يا صحبي، عامل ايه؟",
        "الحمد لله تمام، وأنت؟",
        "خلينا نتقابل قريب",
        "تمام يا وحش",
    ]
    assert message in fallbacks


def test_calculate_delay():
    warmer = AccountWarmer()
    delay = warmer.calculate_delay(10, 20)
    assert 10 <= delay <= 20

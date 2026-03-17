import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.campaign_manager import CampaignManager


@pytest.mark.asyncio
async def test_campaign_manager_init():
    """Test initialization with a mock provider"""
    mock_provider = MagicMock()
    manager = CampaignManager(mock_provider)
    assert manager.service == mock_provider


@pytest.mark.asyncio
async def test_run_smart_campaign_text_only():
    """Test running a campaign with text only"""
    # Setup
    mock_provider = MagicMock()
    # verify_connection is not called in CampaignManager, it assumes service is ready or handles errors.
    # send_whatsapp_message return value: (success: bool, response: dict)
    mock_provider.send_whatsapp_message.return_value = (True, {"id": "123"})

    manager = CampaignManager(mock_provider)

    # Test Data
    numbers = ["201012345678", "201112345678"]
    message = "Hello Test"

    # Mock _is_working_hour to always return True to avoid sleep loop
    with patch.object(CampaignManager, "_is_working_hour", return_value=True):
        # Mock asyncio.sleep to run instantly
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            results = await manager.run_smart_campaign(
                numbers=numbers,
                message=message,
                user_id="test-user",
                instance_name="test-instance",
                delay_min=0,
                delay_max=0,
            )

    # Assertions
    assert results["success"] is True
    assert len(results["details"]) == 2
    assert results["details"][0]["status"] == "sent"
    assert mock_provider.send_whatsapp_message.call_count == 2

    # Verify call arguments
    # First call
    mock_provider.send_whatsapp_message.assert_any_call(
        "201012345678", "Hello Test", instance_name="test-instance"
    )
    # Second call
    mock_provider.send_whatsapp_message.assert_any_call(
        "201112345678", "Hello Test", instance_name="test-instance"
    )


@pytest.mark.asyncio
async def test_run_smart_campaign_with_media():
    """Test running a campaign with media"""
    mock_provider = MagicMock()
    mock_provider.send_whatsapp_message.return_value = (True, {"id": "mediamsg"})

    manager = CampaignManager(mock_provider)

    numbers = ["201000000000"]
    message = "Check this image"
    media_path = "/tmp/image.png"

    with patch.object(CampaignManager, "_is_working_hour", return_value=True):
        with patch("asyncio.sleep", new_callable=AsyncMock):
            results = await manager.run_smart_campaign(
                numbers=numbers,
                message=message,
                user_id="test-user",
                instance_name="test-instance",
                media_file=media_path,
            )

    assert results["details"][0]["status"] == "sent"
    # Verify media arg passed.
    # Note: CampaignManager passes (phone, message, media_path, media_type, instance_name=X)
    mock_provider.send_whatsapp_message.assert_called_once_with(
        "201000000000",
        "Check this image",
        media_path,
        None,
        instance_name="test-instance",
    )


@pytest.mark.asyncio
async def test_campaign_manager_handles_exception():
    """Test that one failure doesn't stop the campaign"""
    mock_provider = MagicMock()
    # First call success, second raises Exception
    mock_provider.send_whatsapp_message.side_effect = [
        (True, {"id": "1"}),
        Exception("Network Error"),
    ]

    manager = CampaignManager(mock_provider)
    numbers = ["201011111111", "201022222222"]

    with patch.object(CampaignManager, "_is_working_hour", return_value=True):
        with patch("asyncio.sleep", new_callable=AsyncMock):
            results = await manager.run_smart_campaign(
                numbers, "Fail Test", user_id="test-user"
            )

    assert len(results["details"]) == 2
    assert results["details"][0]["status"] == "sent"
    assert results["details"][1]["status"] == "error"
    assert "Network Error" in results["details"][1]["error"]


if __name__ == "__main__":
    pytest.main([__file__])

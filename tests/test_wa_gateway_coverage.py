import pytest
from unittest.mock import MagicMock, AsyncMock, patch, mock_open
import sys
import os
import io

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.wa_gateway import WAGateway as CloudService


class TestCloudServiceCoverage:
    """
    Surgical Coverage Test for backend/cloud_service.py
    Target: Increase coverage from 0% to nearly 100%
    """

    @pytest.fixture
    def mock_service(self):
        with patch("backend.cloud_service.os.getenv") as mock_env:
            # Mock env vars
            mock_env.return_value = "mock_value"

            # Since init calls _verify_connection which makes a request,
            # we need to mock requests in init scope or patch the verify method
            with patch("backend.cloud_service.requests.get") as mock_get:
                mock_get.return_value.status_code = 200
                mock_get.return_value.json.return_value = {
                    "instance": {"state": "open"}
                }

                service = CloudService()
                yield service

    def test_init_and_verify_connection(self):
        """Test initialization and connection verification logic"""
        with patch("backend.cloud_service.requests.get") as mock_get:
            # Case 1: Active Connection
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"instance": {"state": "open"}}
            service = CloudService()
            assert service.is_connected is True

            # Case 2: Inactive Connection
            mock_get.return_value.json.return_value = {"instance": {"state": "close"}}
            service._verify_connection()
            assert service.is_connected is False

            # Case 3: Exception
            mock_get.side_effect = Exception("Connect Error")
            service._verify_connection()
            assert service.is_connected is False

    def test_get_qr_code(self, mock_service):
        """Test QR Code retrieval logic"""
        with patch("backend.cloud_service.requests.get") as mock_get:
            # Success Scenarios
            # The method calls state endpoint first, then QR endpoint
            # We mock side_effect to return state response first, then QR response
            mock_get.side_effect = [
                # 1. State check -> returns 'close' to trigger new QR
                MagicMock(
                    status_code=200, json=lambda: {"instance": {"state": "close"}}
                ),
                # 2. QR Request -> returns Base64
                MagicMock(
                    status_code=200,
                    json=lambda: {
                        "base64": "data:image/png;base64,123",
                        "status": "PENDING",
                    },
                ),
            ]

            res = mock_service.get_evolution_qr()
            assert res["success"] is True
            assert "base64" in res["data"]

            # Reset side effect for next assertion
            mock_get.side_effect = None

            # Failure (Already connected)
            mock_service = (
                CloudService()
            )  # Re-init to reset internal state if needed
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"instance": {"state": "open"}}

            res = mock_service.get_evolution_qr()
            assert res["success"] is False
            assert "Already connected" in res["error"]

    def test_get_pairing_code(self, mock_service):
        with patch("backend.cloud_service.requests.get") as mock_get:
            # Success
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"pairingCode": "ABC-123"}
            res = mock_service.get_pairing_code("20100")
            assert res["success"] is True
            assert res["code"] == "ABC-123"

    def test_send_whatsapp_message_text(self, mock_service):
        with patch("backend.cloud_service.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"key": {"id": "MSG1"}}

            # Normal Send
            success, _ = mock_service.send_whatsapp_message("20100", "Hello")
            assert success is True

            # Exception Handling
            mock_post.side_effect = Exception("Net Error")
            success, err = mock_service.send_whatsapp_message("20100", "Hello")
            assert success is False

    @pytest.mark.asyncio
    async def test_run_smart_campaign_integration(self, mock_service):
        """Test the smart campaign integration logic"""
        with patch.object(mock_service, "_is_working_hour", return_value=True):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                with patch.object(
                    mock_service, "_send_evolution_text"
                ) as mock_send_text:
                    mock_send_text.return_value = (True, {"id": "1"})

                    res = await mock_service.run_smart_campaign(
                        numbers=["123"], message="Msg", work_start=0, work_end=24
                    )
                    assert res["success"] is True
                    assert len(res["details"]) == 1

    def test_send_evolution_media_logic(self, mock_service):
        """Test complex media sending logic including compression"""
        with patch("backend.cloud_service.requests.post") as mock_post:
            with patch("backend.cloud_service.os.path.exists", return_value=True):
                with patch("backend.cloud_service.os.path.getsize", return_value=100):
                    # Mock file open
                    with patch("builtins.open", mock_open(read_data=b"image_bytes")):
                        mock_post.return_value.status_code = 200
                        mock_post.return_value.json.return_value = {"sent": True}

                        # Test normal image send
                        success, _ = mock_service.send_whatsapp_message(
                            "20100", "Cap", "img.png"
                        )
                        assert success is True

    def test_set_webhook(self, mock_service):
        with patch("backend.cloud_service.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            res = mock_service.set_evolution_webhook("http://site.com/webhook")
            assert res is True

            # Test Exception
            mock_post.side_effect = Exception("Webhook Fail")
            res = mock_service.set_evolution_webhook("http://site.com/webhook")
            assert res is False

    def test_connection_management(self, mock_service):
        """Cover get_connection_state and logout_instance"""
        with patch("backend.cloud_service.requests.get") as mock_get, patch(
            "backend.cloud_service.requests.delete"
        ) as mock_delete:

            # Connection State - Exception
            mock_get.side_effect = Exception("Conn Error")
            state = mock_service.get_connection_state()
            assert state["instance"]["state"] == "error"

            # Logout - Success
            mock_delete.return_value.status_code = 200
            assert mock_service.logout_instance() is True

            # Logout - Exception
            mock_delete.side_effect = Exception("Logout Fail")
            assert mock_service.logout_instance() is False

    def test_warmup(self, mock_service):
        """Cover warmup logic"""
        with patch.object(mock_service, "_verify_connection", return_value=True):
            with patch.object(mock_service, "set_evolution_webhook", return_value=True):
                mock_service.webhook_url = "http://hook"
                success, msg = mock_service.warmup()
                assert success is True
                assert "Ready" in msg

        with patch.object(mock_service, "_verify_connection", return_value=False):
            success, msg = mock_service.warmup()
            assert success is False

    def test_legacy_features(self, mock_service):
        """Cover get_creation_payload and start_campaign_cloud"""
        # Creation Payload
        mock_service.webhook_url = "http://test/webhook/rec"
        payload = mock_service.get_creation_payload("Instance1")
        assert payload["instanceName"] == "Instance1"
        assert "webhook/whatsapp" in payload["webhook"]

        # Start Campaign Cloud
        with patch.object(mock_service, "_send_evolution_text") as mock_send:
            mock_send.return_value = (True, {})
            res = mock_service.start_campaign_cloud(["123"], "Msg")
            assert res["sent"] == 1
            assert res["success"] is True

    def test_working_hour_logic(self, mock_service):
        """Cover _is_working_hour logic"""
        # Case 1: Standard Day (9 to 17)
        with patch("backend.cloud_service.datetime") as mock_dt:
            mock_dt.now.return_value.hour = 12
            assert mock_service._is_working_hour(9, 17) is True

            mock_dt.now.return_value.hour = 20
            assert mock_service._is_working_hour(9, 17) is False

        # Case 2: Overnight (22 to 6)
        with patch("backend.cloud_service.datetime") as mock_dt:
            mock_dt.now.return_value.hour = 23
            assert mock_service._is_working_hour(22, 6) is True

            mock_dt.now.return_value.hour = 4
            assert mock_service._is_working_hour(22, 6) is True

            mock_dt.now.return_value.hour = 10
            assert mock_service._is_working_hour(22, 6) is False

    def test_group_and_numbers_api(self, mock_service):
        """Cover fetch_all_groups, fetch_group_participants, check_numbers_exist"""
        with patch("backend.cloud_service.requests.get") as mock_get, patch(
            "backend.cloud_service.requests.post"
        ) as mock_post:

            # Fetch Groups
            mock_get.return_value.json.return_value = ["g1", "g2"]
            assert mock_service.fetch_all_groups() == ["g1", "g2"]

            # Fetch Participants
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"participants": ["p1"]}
            res = mock_service.fetch_group_participants("g1")
            assert res["participants"] == ["p1"]

            # Check Numbers
            mock_post.return_value.json.return_value = {"exists": True}
            assert mock_service.check_numbers_exist(["123"]) == {"exists": True}

    def test_ask_ai_cloud(self, mock_service):
        """Cover ask_ai_cloud legacy method"""
        with patch("backend.cloud_service.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"response": "AI says hi"}

            mock_service.key = "abc"  # Set legacy key
            res = mock_service.ask_ai_cloud("Prompt")
            assert res == "AI says hi"

            # Exception
            mock_post.side_effect = Exception("Fail")

    def test_verify_legacy_connection(self, mock_service):
        """Cover _verify_legacy_connection logic (Lines 200-210)"""
        with patch("backend.cloud_service.requests.get") as mock_get:
            # Setup missing attribute to avoid AttributeError in logic
            mock_service.key = "legacy_key"

            # Case 1: Success
            mock_get.return_value.status_code = 200
            mock_service.url = "http://legacy"
            assert mock_service._verify_legacy_connection() is True
            assert mock_service.is_connected is True

            # Case 2: Failure
            mock_get.side_effect = Exception("Down")
            assert mock_service._verify_legacy_connection() is False

    @pytest.mark.asyncio
    async def test_run_smart_campaign_complex_flow(self, mock_service):
        """Cover run_smart_campaign edge cases (Lines 249-283)"""
        # Mock dependencies
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep, patch.object(
            mock_service, "_send_evolution_text"
        ) as mock_send_text, patch.object(
            mock_service, "_send_evolution_media"
        ) as mock_send_media:

            # Setup
            mock_send_text.return_value = (True, "OK")
            mock_send_media.return_value = (True, "OK")

            # Scenario A: Group Link + Working Hours Wait + Progress Callback
            # We mock _is_working_hour to return False first (trigger wait), then True
            with patch.object(
                mock_service, "_is_working_hour", side_effect=[False, True, True]
            ):
                progress = MagicMock()
                res = await mock_service.run_smart_campaign(
                    numbers=["1"],
                    message="Msg",
                    group_link="http://link",
                    progress_callback=progress,
                )

                # Check Wait logic (Line 256-258)
                assert mock_sleep.call_count >= 1
                # Check Group Link (Line 249)
                # Check Group Link (Line 249)
                # Since we use asyncio.to_thread, the mock itself is called synchronously
                mock_send_text.assert_called()
                call_args = mock_send_text.call_args
                assert "http://link" in call_args[0][1]

            # Scenario B: Media Send + Exception Handling (Lines 263, 273)
            mock_send_media.side_effect = Exception("Media Fail")
            with patch.object(mock_service, "_is_working_hour", return_value=True):
                res = await mock_service.run_smart_campaign(
                    numbers=["2"],
                    message="Msg",
                    media_file="img.png",
                    media_type="image",
                )
                assert res["details"][0]["status"] == "error"

    def test_send_media_complex_scenarios(self, mock_service):
        """Cover _send_evolution_media compression and fallback (Lines 347-434)"""
        with patch("backend.cloud_service.requests.post") as mock_post, patch(
            "backend.cloud_service.os.path.exists", return_value=True
        ), patch("backend.cloud_service.os.path.getsize") as mock_size, patch(
            "builtins.open", mock_open(read_data=b"fake_image_data")
        ), patch(
            "backend.cloud_service.base64.b64encode"
        ) as mock_b64:

            mock_b64.return_value.decode.return_value = "BASE64"

            # Case 1: Large Image Compression (Pillow)
            mock_size.return_value = 2 * 1024 * 1024  # 2MB
            # Patch PIL.Image instead of backend.cloud_service.Image to handle local import
            with patch("PIL.Image") as mock_pil:
                mock_img = mock_pil.open.return_value
                mock_img.mode = "RGBA"
                # Crucial: make convert return the same mock object so we can assert thumbnail on it
                mock_img.convert.return_value = mock_img

                mock_post.return_value.status_code = 200
                mock_service._send_evolution_media("123", "Cap", "large.png")

                # Verify resize called
                mock_img.thumbnail.assert_called()

            # Case 2: Video Extension Logic (Line 393)
            # We assume fail on first structure, succeed on fallback (Line 416)
            mock_post.side_effect = [
                MagicMock(status_code=400),  # First try fails
                MagicMock(status_code=200),  # Fallback succeeds
            ]
            # Mock mimetype detection
            with patch("mimetypes.guess_type", return_value=("video/mp4", None)):
                start_size = 100
                mock_size.return_value = start_size

                res, _ = mock_service._send_evolution_media(
                    "123", "Cap", "vid.mp4", media_type="video"
                )
                assert res is True
                # Ensure fallback payload used
                assert mock_post.call_count == 2

            # Case 3: Invalid Type (Line 379)
            res, err = mock_service._send_evolution_media("123", "Cap", 12345)
            assert res is False
            assert "Invalid media type" in err

    def test_misc_exceptions(self, mock_service):
        """Cover remaining exception paths"""
        # send_whatsapp_message generic exception (Line 485)
        with patch.object(
            mock_service, "_send_evolution_text", side_effect=Exception("Gen Fail")
        ):
            res, _ = mock_service.send_whatsapp_message("1", "msg")
            assert res is False

        # check_numbers_exist exception (Line 472)
        with patch(
            "backend.cloud_service.requests.post", side_effect=Exception("Check Fail")
        ):
            res = mock_service.check_numbers_exist(["1"])
            assert res == []


if __name__ == "__main__":
    pytest.main([__file__])

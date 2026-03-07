import pytest
import json
from unittest.mock import MagicMock, patch, mock_open, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.webhook_handler import router

# Create a proper FastAPI app and include the router
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestWebhookHandlerSurgical:
    """
    Surgical Tests for backend/webhook_handler.py
    Focuses on currently active endpoints:
    - /webhook/health
    - /webhook/whatsapp
    - /webhook/test
    """

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/webhook/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_webhook_receive_success(self):
        """Test receiving a valid WhatsApp webhook (Evolution API v2)"""
        payload = {
            "event": "messages.upsert",
            "data": {
                "key": {"remoteJid": "123@s.whatsapp.net", "fromMe": False},
                "pushName": "Ahmed",
                "message": {"conversation": "Hello"},
            },
        }
        response = client.post("/webhook/whatsapp", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "processing"

    def test_webhook_test_success(self):
        """Test the manual testing endpoint /webhook/test"""
        payload = {
            "key": {"remoteJid": "123@s.whatsapp.net", "fromMe": False},
            "message": {"conversation": "This is a test"},
        }
        # Note: evolution-api sometimes wraps in data, but webhook/test expects the raw message part often
        # based on extraction logic. Let's provide a structure that satisfies extract_message_info.
        payload = {
            "data": {
                "key": {"remoteJid": "123@s.whatsapp.net", "fromMe": False},
                "message": {"conversation": "Hi"},
            }
        }
        response = client.post("/webhook/test", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["extracted"]["message_text"] == "Hi"

    # =================================================================
    # ❌ FAILURE & ERROR HANDLING TESTS
    # =================================================================

    def test_whatsapp_webhook_json_error(self):
        """Test invalid JSON handling"""
        # TestClient doesn't easily send malformed JSON via 'json' param.
        # We can send raw content.
        response = client.post(
            "/webhook/whatsapp",
            content="invalid{json}",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400
        assert response.json()["status"] == "error"

    def test_webhook_test_exception(self):
        """Cover line 339-340: Exception handling in test endpoint"""
        with patch(
            "backend.webhook_handler.extract_message_info",
            side_effect=Exception("Extraction Fail"),
        ):
            response = client.post("/webhook/test", json={})
            assert response.json()["success"] is False
            assert "Extraction Fail" in response.json()["error"]

    @pytest.mark.asyncio
    async def test_process_whatsapp_message_pause_logic(self):
        """Test Step 2.1: Human response triggers bot pause"""
        from backend.webhook_handler import process_whatsapp_message

        payload = {
            "data": {
                "key": {"remoteJid": "123@s.whatsapp.net", "fromMe": True},  # FROM ME
                "message": {"conversation": "I am a human agent"},
            }
        }

        with patch("backend.webhook_handler.pause_bot_for_customer") as mock_pause:
            await process_whatsapp_message(payload)
            mock_pause.assert_called_with("123", hours=pytest.approx(4, rel=1))

    @pytest.mark.asyncio
    async def test_process_whatsapp_message_no_action(self):
        """Test case where no action should be taken (no text, no media)"""
        from backend.webhook_handler import process_whatsapp_message

        payload = {
            "data": {
                "key": {"remoteJid": "123@s.whatsapp.net", "fromMe": False},
                "message": {},  # Empty
            }
        }

        with patch("backend.webhook_handler.get_customer_by_phone") as mock_db:
            await process_whatsapp_message(payload)
            mock_db.assert_not_called()

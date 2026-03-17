
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from backend.baileys_client import BaileysClient

class TestBaileysClientSurgical:

    @pytest.fixture
    def client_evo(self):
        with patch.dict('os.environ', {'WHATSAPP_PROVIDER': 'evolution'}):
            return BaileysClient()

    @pytest.fixture
    def client_legacy(self):
        with patch.dict('os.environ', {'WHATSAPP_PROVIDER': 'baileys'}):
            return BaileysClient()

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_send_message_evolution_success(self, client_evo):
        """اختبار إرسال رسالة عبر مزود Evolution بنجاح"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "123"}
        
        with patch('httpx.AsyncClient.post', AsyncMock(return_value=mock_response)):
            res = await client_evo.send_message("123", "Hello")
            assert res['success'] is True
            assert res['data']['key'] == "123"

    @pytest.mark.asyncio
    async def test_send_message_legacy_success(self, client_legacy):
        """اختبار إرسال رسالة عبر مزود Baileys القديم بنجاح"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "sent"}
        
        with patch('httpx.AsyncClient.post', AsyncMock(return_value=mock_response)):
            res = await client_legacy.send_message("123", "Hello")
            assert res['success'] is True

    @pytest.mark.asyncio
    async def test_get_status_connected_evolution(self, client_evo):
        """اختبار جلب حالة الاتصال لمزود Evolution"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"instance": {"state": "open"}}
        
        with patch('httpx.AsyncClient.get', AsyncMock(return_value=mock_response)):
            res = await client_evo.get_status()
            assert res['connected'] is True
            assert res['state'] == 'open'

    # =================================================================
    # ❌ LOGIC FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_send_message_unauthorized_error(self, client_evo):
        """اختبار خطأ في المصادقة (Unauthorized)"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch('httpx.AsyncClient.post', AsyncMock(return_value=mock_response)):
            res = await client_evo.send_message("123", "Hello")
            assert res['success'] is False
            assert "Status 401" in res['error']

    @pytest.mark.asyncio
    async def test_get_status_disconnected_legacy(self, client_legacy):
        """اختبار حالة غير متصل لمزود قديم"""
        mock_response = MagicMock()
        mock_response.status_code = 503
        
        with patch('httpx.AsyncClient.get', AsyncMock(return_value=mock_response)):
            res = await client_legacy.get_status()
            assert res['connected'] is False

    # =================================================================
    # 💥 SYSTEM FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_send_message_network_exception(self, client_evo):
        """اختبار حدوث خطأ في الشبكة (Timeout)"""
        with patch('httpx.AsyncClient.post', AsyncMock(side_effect=Exception("Timeout"))):
            res = await client_evo.send_message("123", "Hello")
            assert res['success'] is False
            assert "Timeout" in res['error']

    @pytest.mark.asyncio
    async def test_get_status_exception(self, client_evo):
        """تغطية الـ except في جلب الحالة"""
        with patch('httpx.AsyncClient.get', AsyncMock(side_effect=Exception("Down"))):
            res = await client_evo.get_status()
            assert res['connected'] is False
            assert "Down" in res['error']

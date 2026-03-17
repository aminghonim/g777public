import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from backend.campaign_manager import CampaignManager
from datetime import datetime


class TestCampaignManagerSurgical:

    @pytest.fixture
    def manager(self):
        mock_service = MagicMock()
        mock_service.send_whatsapp_message = MagicMock(return_value=(True, "OK"))
        return CampaignManager(mock_service)

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    @patch("asyncio.sleep", AsyncMock())
    async def test_run_smart_campaign_success(self, manager):
        """اختبار تشغيل حملة ذكية بنجاح"""
        numbers = ["123", "456"]
        res = await manager.run_smart_campaign(
            numbers, "Hello", "test-user", delay_min=0, delay_max=0
        )

        assert res["success"] is True
        assert len(res["details"]) == 2
        assert manager.service.send_whatsapp_message.call_count == 2

    @pytest.mark.asyncio
    @patch("asyncio.sleep", AsyncMock())
    async def test_run_smart_campaign_with_media(self, manager):
        """اختبار الإرسال مع المرفقات"""
        await manager.run_smart_campaign(
            ["1"], "msg", "test-user", media_file="path/to/img.jpg"
        )

        args, kwargs = manager.service.send_whatsapp_message.call_args
        assert args[2] == "path/to/img.jpg"

    def test_is_working_hour_logic(self, manager):
        """اختبار منطق ساعات العمل"""
        # Case: Current hour is 12 (Noon), Working hours 9-22
        # The logic is: start <= current_hour < end
        # 9 <= 12 < 22 -> True

        # To properly test, we need to patch datetime.now()
        with patch("backend.campaign_manager.datetime") as mock_datetime:
            # Daytime test: 12 PM should be inside 9-22
            mock_datetime.now.return_value = MagicMock(hour=12)
            assert manager._is_working_hour(9, 22) is True

            # Night test: 23 (11 PM) should be outside 9-22
            mock_datetime.now.return_value = MagicMock(hour=23)
            assert manager._is_working_hour(9, 22) is False

        # Case: Overnight shift (10 PM to 6 AM)
        with patch("backend.campaign_manager.datetime") as mock_datetime:
            # 2 AM should be inside 22-6 (overnight)
            mock_datetime.now.return_value = MagicMock(hour=2)
            assert manager._is_working_hour(22, 6) is True

            # 12 PM should be outside 22-6 (overnight)
            mock_datetime.now.return_value = MagicMock(hour=12)
            assert manager._is_working_hour(22, 6) is False

    # =================================================================
    # ❌ LOGIC FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_working_hour_sleep_cycle(self, manager):
        """اختبار الانتظار عند التواجد خارج ساعات العمل"""
        # محاكاة: المرة الأولى خارج ساعات العمل، المرة الثانية داخلها
        with patch.object(
            manager, "_is_working_hour", side_effect=[False, True, True]
        ), patch("asyncio.sleep", AsyncMock()) as mock_sleep:

            await manager.run_smart_campaign(["1"], "msg", "test-user")

            # التأكد من أنه نام (900 ثانية = 15 دقيقة)
            mock_sleep.assert_any_call(900)

    # =================================================================
    # 💥 SYSTEM FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    @patch("asyncio.sleep", AsyncMock())
    async def test_send_logic_exception_handling(self, manager):
        """تغطية الـ except في حلقة الإرسال"""
        manager.service.send_whatsapp_message.side_effect = Exception("Service Crashed")

        res = await manager.run_smart_campaign(["1"], "msg", "test-user")
        assert res["details"][0]["status"] == "error"
        assert "Service Crashed" in res["details"][0]["error"]

    @pytest.mark.asyncio
    @patch("asyncio.sleep", AsyncMock())
    async def test_progress_callback_success(self, manager):
        """اختبار استدعاء الـ callback بنجاح"""
        mock_callback = MagicMock()

        await manager.run_smart_campaign(
            ["1"], "msg", "test-user", progress_callback=mock_callback
        )
        assert mock_callback.called

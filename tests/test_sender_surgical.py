import pytest
import time
from unittest.mock import MagicMock, patch
from backend.whatsapp_sender import WhatsAppSender


class TestSenderSurgical:

    @pytest.fixture
    def sender(self):
        with patch(
            "backend.whatsapp_sender.AzureCloudService"
        ) as mock_cloud_class, patch("backend.whatsapp_sender.db_manager") as mock_db:

            # Setup Cloud Mock
            mock_instance = mock_cloud_class.return_value
            mock_instance.warmup = MagicMock(return_value=(True, "Server Ready"))
            mock_instance.start_campaign_cloud = MagicMock(
                return_value={"success": True}
            )

            # Setup DB Mock (SAAS-013 Resilience)
            mock_db.get_user_quota_info.return_value = {
                "daily_limit": 1000,
                "message_count": 0,
                "max_instances": 1,
                "instance_count": 0,
            }

            sender = WhatsAppSender()
            sender.db_manager = mock_db  # Ensure it uses the mock
            return sender

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_replace_variables_success(self, sender):
        """اختبار استبدال المتغيرات في الرسالة"""
        msg = "Hello {name}"
        data = {"name": "Ahmed"}
        assert await sender._process_message(msg, data) == "Hello Ahmed"
        assert await sender._process_message("H {Name}", data) == "H Ahmed"
        assert await sender._process_message("H {NAME}", data) == "H Ahmed"
        assert await sender._process_message(msg, "not_a_dict") == "Hello العميل"
        assert await sender._process_message(msg, {}) == "Hello العميل"

    @patch("time.sleep", return_value=None)
    def test_run_campaign_success(self, mock_sleep, sender):
        """اختبار تشغيل حملة كاملة بنجاح"""
        mock_members = [
            {"phone": "123", "name": "User1"},
            {"phone": "456", "name": "User2"},
        ]

        with patch(
            "backend.excel_processor.ExcelProcessor.read_contacts",
            return_value=mock_members,
        ):
            sender.run_campaign("fake.xlsx", "Sheet1", ["Hello {name}"])

            assert sender.cloud.start_campaign_cloud.call_count == 2
            assert sender.is_running is False

    # =================================================================
    # ❌ LOGIC FAILURE STATE TESTS
    # =================================================================

    @patch("time.sleep", return_value=None)
    def test_stop_campaign_midway(self, mock_sleep, sender):
        """اختبار إيقاف الحملة في المنتصف"""
        mock_members = [{"phone": "1"}, {"phone": "2"}, {"phone": "3"}]

        def stop_on_second(*args, **kwargs):
            if sender.cloud.start_campaign_cloud.call_count >= 1:
                sender.stop_campaign()
            return {"success": True}

        sender.cloud.start_campaign_cloud = MagicMock(side_effect=stop_on_second)

        with patch(
            "backend.excel_processor.ExcelProcessor.read_contacts",
            return_value=mock_members,
        ):
            sender.run_campaign("fake.xlsx", "Sheet1", ["msg"])
            assert sender.cloud.start_campaign_cloud.call_count < 3

    # =================================================================
    # 💥 SYSTEM FAILURE STATE TESTS
    # =================================================================

    @patch("time.sleep", return_value=None)
    def test_run_campaign_api_error_details_handling(self, mock_sleep, sender):
        """اختبار التعامل مع حالات خطأ متنوعة من الـ API"""
        mock_members = [{"phone": "123"}]

        sender.cloud.start_campaign_cloud = MagicMock(
            return_value={"success": False, "details": [{"error": "Rate Limit"}]}
        )

        with patch(
            "backend.excel_processor.ExcelProcessor.read_contacts",
            return_value=mock_members,
        ):
            sender.run_campaign("fake.xlsx", "Sheet1", ["msg"])
            assert sender.is_running is False

    @patch("time.sleep", return_value=None)
    def test_run_campaign_exception_in_loop(self, mock_sleep, sender):
        """اختبار الصمود امام استثناء مفاجئ داخل حلقة الإرسال"""
        mock_members = [{"phone": "123"}]
        sender.cloud.start_campaign_cloud = MagicMock(
            side_effect=Exception("Network Timeout")
        )

        with patch(
            "backend.excel_processor.ExcelProcessor.read_contacts",
            return_value=mock_members,
        ):
            sender.run_campaign("fake.xlsx", "Sheet1", ["msg"])
            assert sender.is_running is False

    @patch("time.sleep", return_value=None)
    def test_run_campaign_excel_load_failure(self, mock_sleep, sender):
        """تغطية الـ except الكلي للحملة عند فشل قراءة الملف"""
        with patch(
            "backend.excel_processor.ExcelProcessor.read_contacts",
            side_effect=Exception("File Locked"),
        ):
            sender.run_campaign("locked.xlsx", "Sheet1", ["msg"])
            assert sender.is_running is False

    def test_callback_error_resilience(self, sender):
        """التأكد من أن خطأ في وظيفة الـ Callback لا يعطل الإرسال"""

        def bad_callback(msg):
            raise Exception("UI Crash")

        sender.set_callback(bad_callback)
        sender.log("Test Log Notification")

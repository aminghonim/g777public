import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from backend.message_processor import process_ai_response, extract_message_info


class TestMessageProcessorSurgical:

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_process_ai_response_full_pipeline_success(self):
        """اختبار دورة إنتاج الرد كاملة من الذكاء الاصطناعي حتى التحسين البشري"""
        with patch(
            "backend.message_processor.ai_engine.generate_response",
            AsyncMock(return_value="Robotic Answer"),
        ), patch(
            "backend.message_processor.BrainTrainer.humanize_bot_response",
            AsyncMock(return_value="Human Answer"),
        ), patch(
            "backend.message_processor.get_db_cursor"
        ) as mock_db:

            # محاكاة حفظ ناجح في قاعدة البيانات
            mock_db.return_value.__enter__.return_value.execute = MagicMock()

            res = await process_ai_response("Hello", "123", "History")
            assert res == "Human Answer"

    def test_extract_message_info_variants(self):
        """اختبار مرونة استخراج البيانات من أشكال JSON مختلفة"""
        # Case 1: Evolution API v2 structure (Nested in data)
        payload_v2 = {
            "data": {
                "key": {"remoteJid": "1@s.net", "fromMe": False},
                "message": {"conversation": "Hi"},
            }
        }
        txt, jid, me, m_type, m_meta = extract_message_info(payload_v2)
        assert txt == "Hi" and jid == "1@s.net" and me is False and m_type is None

        # Case 2: Extended text message
        payload_ext = {
            "data": {
                "message": {"extendedTextMessage": {"text": "Long msg"}},
                "key": {"fromMe": True},
            }
        }
        txt, _, me, _, _ = extract_message_info(payload_ext)
        assert txt == "Long msg" and me is True

        # Case 3: Flat structure (Fallback)
        payload_flat = {"text": "Flat Hi", "remoteJid": "2@s.net", "fromMe": False}
        txt, jid, _, _, _ = extract_message_info(payload_flat)
        assert txt == "Flat Hi" and jid == "2@s.net"

        # Case 4: Other text field
        payload_other = {"data": {"text": "direct text"}}
        txt, _, _, _, _ = extract_message_info(payload_other)
        assert txt == "direct text"

    # =================================================================
    # ❌ LOGIC FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_process_ai_response_empty_raw(self):
        """حالة فشل AI في توليد أي رد"""
        with patch(
            "backend.message_processor.ai_engine.generate_response",
            AsyncMock(return_value=None),
        ):
            res = await process_ai_response("hi", "123", "")
            assert res is None

    def test_extract_message_info_empty_payload(self):
        """حالة استسلام حمولة فارغة"""
        txt, jid, me, m_type, m_meta = extract_message_info({})
        assert txt == "" and jid == "" and me is False and m_type is None

    # =================================================================
    # 💥 SYSTEM FAILURE STATE TESTS (Covering Exception Handlers)
    # =================================================================

    @pytest.mark.asyncio
    async def test_process_ai_response_db_error_resilience(self):
        """التأكد من أن فشل الـ DB لا يعطل الرد النهائي (Resilience)"""
        with patch(
            "backend.message_processor.ai_engine.generate_response",
            AsyncMock(return_value="Robotic"),
        ), patch(
            "backend.message_processor.BrainTrainer.humanize_bot_response",
            AsyncMock(return_value="Human"),
        ), patch(
            "backend.message_processor.get_db_cursor"
        ) as mock_db:

            # محاكاة خطأ في الـ SQL
            mock_db.return_value.__enter__.return_value.execute.side_effect = Exception(
                "DB Crash"
            )

            res = await process_ai_response("hi", "1", "hist")
            assert res == "Human"  # الرد يجب أن يصل رغم فشل الحفظ

    @pytest.mark.asyncio
    async def test_process_ai_response_crash_handling(self):
        """تغطية الـ except الكلي لوظيفة المعالجة"""
        with patch(
            "backend.message_processor.ai_engine.generate_response",
            side_effect=Exception("Total Crash"),
        ):
            res = await process_ai_response("msg", "1", "")
            assert res is None

    def test_extract_message_info_nested_text(self):
        """تغطية مسارات الـ get المتعددة"""
        payload = {"data": {"message": {"text": "direct text in message obj"}}}
        txt, _, _, _, _ = extract_message_info(payload)
        assert txt == "direct text in message obj"

        payload_content = {"data": {"content": "content text"}}
        txt, _, _, _, _ = extract_message_info(payload_content)
        assert txt == "content text"

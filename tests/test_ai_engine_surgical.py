import pytest
import os
import json
from unittest.mock import MagicMock, patch, AsyncMock, mock_open
from backend.ai_engine import AIEngine


class TestAIEngineSurgical:

    @pytest.fixture
    def ai(self):
        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock()
        with patch("google.genai.Client", return_value=mock_client):
            with patch("backend.ai_engine.is_excluded", return_value=False):
                engine = AIEngine()
                return engine

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_analyze_intent_success(self, ai):
        """اختبار تصنيف النية بنجاح"""
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {"is_business": True, "intent": "pricing_request"}
        )

        ai.client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        res = await ai.analyze_intent("عايز اعرف الاسعار")
        assert res["is_business"] is True
        assert res["intent"] == "pricing_request"

    @pytest.mark.asyncio
    async def test_extract_and_update_info_success(self, ai):
        """تغطية منطق استخراج المعلومات وتحديث الملف الشخصي"""
        customer = {
            "phone": "123",
            "missing_fields": ["name", "location"],
            "custom_data": {},
        }
        mock_response = MagicMock()
        mock_response.text = json.dumps({"name": "Omar"})
        ai.client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        # Patch where the functions are imported FROM (db_service module)
        with patch("backend.ai_engine.AIEngine._get_settings", return_value={}):
            # Also patch the actual import inside the function
            with patch.dict("sys.modules", {"backend.db_service": MagicMock()}):
                import sys

                sys.modules["backend.db_service"].mark_field_collected = MagicMock()
                sys.modules["backend.db_service"].update_customer = MagicMock()

                updated = await ai.extract_and_update_info("I am Omar", customer)

                # The function should update the customer dict
                assert updated.get("name") == "Omar" or "name" not in updated.get(
                    "missing_fields", []
                )

    @pytest.mark.asyncio
    async def test_generate_response_training_mode(self, ai):
        """تغطية وضع التدريب (بدون أمثلة تعليمية)"""
        with patch("backend.ai_engine.get_customer_by_phone", return_value=None), patch(
            "backend.ai_engine.is_excluded", return_value=False
        ), patch("backend.ai_engine.get_tenant_settings", return_value={}), patch(
            "backend.ai_engine.get_system_prompt", return_value="prompt"
        ), patch(
            "backend.ai_engine.format_offerings_for_prompt", return_value="offerings"
        ), patch(
            "builtins.open", MagicMock(side_effect=FileNotFoundError())
        ):  # Force KB load fail -> Fallback

            mock_response = MagicMock()
            mock_response.text = "Training Response"
            ai.client.aio.models.generate_content = AsyncMock(
                return_value=mock_response
            )

            res = await ai.generate_response("test", "TRAINING_MODE")
            assert "Training Response" in res

    @pytest.mark.asyncio
    async def test_generate_response_normal_flow(self, ai):
        """تغطية الرد الطبيعي مع تحميل الـ KB بنجاح"""
        kb_data = json.dumps({"trips": [], "faq": {}})
        with patch(
            "backend.ai_engine.get_customer_by_phone", return_value={"name": "User"}
        ), patch("backend.ai_engine.is_excluded", return_value=False), patch(
            "backend.ai_engine.get_training_samples", return_value="Samples"
        ), patch(
            "builtins.open", mock_open(read_data=kb_data)
        ):

            mock_response = MagicMock()
            mock_response.text = "AI Response"
            ai.client.aio.models.generate_content = AsyncMock(
                return_value=mock_response
            )

            res = await ai.generate_response("hi", "123")
            assert "AI Response" in res

    def test_load_instructions_failure(self):
        """تغطية فشل تحميل ملف التعليمات"""
        real_open = open

        def open_mock(filename, *args, **kwargs):
            if "ai_instructions.yaml" in str(filename):
                raise Exception("YAML Missing")
            return real_open(filename, *args, **kwargs)

        with patch("builtins.open", side_effect=open_mock):
            engine = AIEngine()
            assert engine.instructions == {}

    # =================================================================
    # ❌ LOGIC FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_generate_response_excluded_user(self, ai):
        """التأكد من عدم الرد على المستخدمين المستبعدين"""
        with patch("backend.ai_engine.is_excluded", return_value=True):
            res = await ai.generate_response("hi", "123")
            assert res == ""

    @pytest.mark.asyncio
    async def test_extract_and_update_info_empty_missing(self, ai):
        """التأكد من عدم عمل الاستخراج إذا لم يكن هناك حقول ناقصة"""
        customer = {"phone": "123", "missing_fields": []}
        updated = await ai.extract_and_update_info("hi", customer)
        assert updated == customer

    @pytest.mark.asyncio
    async def test_analyze_intent_json_cleanup(self, ai):
        """Test striping of markdown code blocks"""
        mock_response = MagicMock()
        mock_response.text = '```json\n{"intent": "test"}\n```'
        ai.client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        res = await ai.analyze_intent("msg")
        assert res["intent"] == "test"

    # =================================================================
    # 💥 SYSTEM FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_generate_response_api_error(self, ai):
        """تغطية الـ except في مولد الردود"""
        with patch("backend.ai_engine.get_customer_by_phone", return_value=None), patch(
            "backend.ai_engine.is_excluded", return_value=False
        ), patch("builtins.open", MagicMock(side_effect=FileNotFoundError())):

            ai.client.aio.models.generate_content = AsyncMock(
                side_effect=Exception("Gemini Offline")
            )

            res = await ai.generate_response("message", "user_phone")
            assert "عذراً" in res or "System Error" in res

    @pytest.mark.asyncio
    async def test_extract_and_update_exception(self, ai):
        """تغطية الـ except في الاستخراج"""
        customer = {"phone": "123", "missing_fields": ["name"]}
        ai.client.aio.models.generate_content = AsyncMock(
            side_effect=Exception("Fatal")
        )
        res = await ai.extract_and_update_info("msg", customer)
        assert res == customer  # Should return original on error

    @pytest.mark.asyncio
    async def test_summarize_customer_exception(self, ai):
        """تغطية الـ except في وظيفة التلخيص"""
        with patch("backend.ai_engine.get_system_prompt", return_value="prompt"):
            ai.client.aio.models.generate_content = AsyncMock(
                side_effect=Exception("Timeout")
            )
            res = await ai.summarize_customer("text")
            assert res == ""

    @pytest.mark.asyncio
    async def test_analyze_intent_exception(self, ai):
        """تغطية الـ except في وضع الـ analyze"""
        ai.client.aio.models.generate_content = AsyncMock(
            side_effect=Exception("Fatal")
        )
        res = await ai.analyze_intent("msg")
        assert res["intent"] == "unknown"

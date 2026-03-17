import pytest
import os
import json
from unittest.mock import MagicMock, patch, AsyncMock, mock_open



class TestAIEngineSurgical:

    @pytest.fixture
    def ai(self):
        mock_client = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock()
        mock_mcp = MagicMock()
        mock_mcp.get_tools_definitions = AsyncMock(return_value=[])
        
        # Patch the function itself in the class, the instance in the modules, AND the class itself
        with patch("google.genai.Client", return_value=mock_client), \
             patch("backend.mcp_manager.MCPManager.get_tools_definitions", AsyncMock(return_value=[])), \
             patch("backend.mcp_manager.mcp_manager", mock_mcp), \
             patch("backend.ai_engine.mcp_manager", mock_mcp), \
             patch("backend.agents.orchestrator.mcp_manager", mock_mcp), \
             patch("backend.agents.orchestrator.VectorStoreManager", MagicMock()), \
             patch("backend.agents.orchestrator.SystemMonitor", MagicMock()):
            with patch("backend.ai_engine.is_excluded", return_value=False), \
                 patch("google.genai.Client", return_value=mock_client):
                from backend.ai_engine import AIEngine
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

        # Patch where the functions are imported FROM
        with patch("backend.ai_engine.get_tenant_settings", return_value={}):
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
        real_open = open
        def open_side_effect(path, *args, **kwargs):
            if "trips_db.json" in str(path):
                raise FileNotFoundError()
            return real_open(path, *args, **kwargs)

        with patch(
            "backend.ai_engine.is_excluded", return_value=False
        ), patch("backend.ai_engine.get_tenant_settings", return_value={}), patch(
            "backend.ai_engine.get_system_prompt", return_value="prompt"
        ), patch(
            "builtins.open", side_effect=open_side_effect
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
        real_open = open
        def open_side_effect(path, *args, **kwargs):
            if "trips_db.json" in str(path):
                return mock_open(read_data=kb_data)(path, *args, **kwargs)
            return real_open(path, *args, **kwargs)

        with patch("backend.ai_engine.is_excluded", return_value=False), patch(
            "builtins.open", side_effect=open_side_effect
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
            from backend.ai_engine import AIEngine
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
        real_open = open
        def open_side_effect(path, *args, **kwargs):
            if "trips_db.json" in str(path):
                raise FileNotFoundError()
            return real_open(path, *args, **kwargs)

        with patch(
            "backend.ai_engine.is_excluded", return_value=False
        ), patch("builtins.open", side_effect=open_side_effect):

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

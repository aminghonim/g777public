
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

class TestBrainTrainerSurgical:

    @pytest.fixture
    def trainer(self):
        with patch('backend.brain_trainer.UnifiedAIClient') as mock_ai_class:
            mock_instance = mock_ai_class.return_value
            mock_instance.generate_response = AsyncMock(return_value="Humanized Response")
            from backend.brain_trainer import BrainTrainer
            return BrainTrainer()

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_humanize_bot_response_success(self, trainer):
        """اختبار تحويل الرد الآلي لرد بشري"""
        trainer.ai.generate_response = AsyncMock(return_value="يا فندم...")
        res = await trainer.humanize_bot_response("السلام عليكم", "مرحباً بك")
        assert "فندم" in res

    @pytest.mark.asyncio
    async def test_train_on_questions_success(self, trainer):
        """اختبار دورة تدريبية كاملة"""
        with patch.object(trainer, '_ensure_table_exists'), \
             patch('backend.brain_trainer.ai_engine', new_callable=AsyncMock) as mock_engine, \
             patch('backend.brain_trainer.get_db_cursor') as mock_cursor:
            
            mock_engine.generate_response.return_value = "Raw Response"
            mock_cursor.return_value.__enter__.return_value = MagicMock()
            
            await trainer.train_on_questions(["سؤال تجريبي"])
            assert mock_engine.generate_response.called

    def test_ensure_table_exists_success(self, trainer):
        """اختبار إنشاء جدول التدريب"""
        mock_cursor = MagicMock()
        with patch('backend.brain_trainer.get_db_cursor') as mock_get_cursor:
            mock_get_cursor.return_value.__enter__.return_value = mock_cursor
            mock_get_cursor.return_value.__exit__ = MagicMock(return_value=False)
            trainer._ensure_table_exists()
            mock_cursor.execute.assert_called_once()

    # =================================================================
    # ❌ LOGIC FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_humanize_bot_response_empty_robotic(self, trainer):
        """حالة الرد الآلي الفارغ"""
        trainer.ai.generate_response = AsyncMock(return_value="Fallback")
        res = await trainer.humanize_bot_response("q", "")
        assert res == "Fallback"

    def test_ensure_table_exists_no_cursor(self, trainer):
        """اختبار التصرف عند فشل الاتصال بالداتابيز"""
        with patch('backend.brain_trainer.get_db_cursor') as mock_get_cursor:
            mock_get_cursor.return_value.__enter__.return_value = None
            mock_get_cursor.return_value.__exit__ = MagicMock(return_value=False)
            # Should return early without crashing
            trainer._ensure_table_exists()

    # =================================================================
    # 💥 SYSTEM FAILURE STATE TESTS
    # =================================================================

    @pytest.mark.asyncio
    async def test_humanize_bot_response_exception(self, trainer):
        """تغطية الـ except عند فشل الـ AI"""
        trainer.ai.generate_response = AsyncMock(side_effect=Exception("AI Service Down"))
        with pytest.raises(Exception):
            await trainer.humanize_bot_response("q", "r")

    @pytest.mark.asyncio
    async def test_train_on_questions_db_error(self, trainer):
        """تغطية حالة فشل حفظ النتائج في الداتابيز"""
        with patch.object(trainer, '_ensure_table_exists'), \
             patch('backend.brain_trainer.ai_engine', new_callable=AsyncMock) as mock_engine, \
             patch('backend.brain_trainer.get_db_cursor') as mock_cursor:
            
            mock_engine.generate_response.return_value = "Raw"
            mock_cursor.return_value.__enter__.return_value = MagicMock(execute=MagicMock(side_effect=Exception("DB Error")))
            
            with pytest.raises(Exception):
                await trainer.train_on_questions(["سؤال"])

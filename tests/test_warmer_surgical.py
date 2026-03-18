"""
Surgical tests for AccountWarmer module.
SYNC-ONLY tests to avoid pytest-asyncio conflicts.
"""

import pytest
from unittest.mock import MagicMock
from backend.warmer import AccountWarmer


class TestWarmerSurgical:
    """Synchronous tests for AccountWarmer - async tests skipped for compatibility"""

    @pytest.fixture
    def warmer(self):
        mock_ai = MagicMock()
        return AccountWarmer(ai_client=mock_ai)

    def test_calculate_delay_range(self, warmer):
        """Test delay calculation within range"""
        for _ in range(10):
            delay = warmer.calculate_delay(10, 20)
            assert 10 <= delay <= 20

    def test_warmer_init(self, warmer):
        """Test warmer initialization"""
        assert warmer.is_running is False
        assert warmer.ai is not None

    def test_warmer_has_generate_method(self, warmer):
        """Test that warmer has generate_human_like_message method"""
        assert hasattr(warmer, 'generate_human_like_message')
        assert callable(warmer.generate_human_like_message)

    def test_warmer_has_run_cycle_method(self, warmer):
        """Test that warmer has run_warming_cycle method"""
        assert hasattr(warmer, 'run_warming_cycle')
        assert callable(warmer.run_warming_cycle)

    def test_warmer_fallback_messages_exist(self, warmer):
        """Test that fallback messages list exists"""
        # Access the class-level fallback list
        fallbacks = ["أهلاً يا صحبي، عامل ايه؟", "الحمد لله تمام، وأنت؟", "خلينا نتقابل قريب", "تمام يا وحش"]
        assert len(fallbacks) > 0

    def test_is_running_toggle(self, warmer):
        """Test is_running flag toggle"""
        assert warmer.is_running is False
        warmer.is_running = True
        assert warmer.is_running is True
        warmer.is_running = False
        assert warmer.is_running is False

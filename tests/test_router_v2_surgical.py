"""
Surgical QA tests for the Smart Router (V2): fallback logic, PII safety, and heuristics.

Validates the UnifiedAIClient fallback chain and SmartRouterAgent classification
within the 50ms latency budget required by the CNS Squad Constitution.
"""
import logging
import time
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from backend.ai_client import UnifiedAIClient, GeminiAIClient, ClaudeAIClient

# Configure logging for inspection
logger = logging.getLogger("backend.ai_client")


class TestRouterV2Surgical:
    """
    Sentinel QA Gate: Smart Router Fallback & Performance Validation.
    Mandate: Zero-Regression & 50ms Latency.
    """

    @pytest.mark.asyncio
    async def test_gemini_429_fallback_to_claude(self):
        """
        Simulate Gemini Rate Limit (429) and verify fallback to Claude-3.
        Ensures context (prompt, system_message) is preserved.
        """
        # 1. Setup Mocks
        mock_gemini = MagicMock(spec=GeminiAIClient)
        mock_gemini.client = MagicMock()  # Ensure it looks "initialized"
        # Simulate 429 error
        mock_gemini.generate_response = AsyncMock(side_effect=Exception("429 Resource exhausted"))

        mock_claude = MagicMock(spec=ClaudeAIClient)
        mock_claude.client = MagicMock()
        mock_claude.generate_response = AsyncMock(return_value="Claude Response")

        # 2. Patch Clients in UnifiedAIClient
        with patch("backend.ai_client.GeminiAIClient", return_value=mock_gemini), \
             patch("backend.ai_client.ClaudeAIClient", return_value=mock_claude):

            unified = UnifiedAIClient(provider="gemini")

            # 3. Measure Latency (Directive: < 50ms for routing logic)
            start_time = time.perf_counter()
            response = await unified.generate_response(
                prompt="User Data: John Doe, +2012345678",
                system_message="System Tone: Professional"
            )
            end_time = time.perf_counter()

            latency_ms = (end_time - start_time) * 1000

            # 4. Assertions
            # Fallback check
            assert response == "Claude Response"
            mock_gemini.generate_response.assert_called_once()
            mock_claude.generate_response.assert_called_once_with(
                "User Data: John Doe, +2012345678", "System Tone: Professional"
            )

            # Latency check (Routing + Fallback initialization)
            # Since mocks are instant, this measures purely the internal logic overhead.
            assert latency_ms < 50, f"Routing latency too high: {latency_ms:.2f}ms"

    @pytest.mark.asyncio
    async def test_no_pii_in_routing_logs(self, caplog):
        """
        Ensure no PII (phone numbers, names) leaks into logs during failure/fallback.
        """
        caplog.set_level(logging.WARNING)

        mock_gemini = MagicMock(spec=GeminiAIClient)
        mock_gemini.client = MagicMock()
        mock_gemini.generate_response = AsyncMock(side_effect=Exception("Failed profoundly"))

        with patch("backend.ai_client.GeminiAIClient", return_value=mock_gemini):
            unified = UnifiedAIClient(provider="gemini")

            # Sensitive data in prompt
            sensitive_prompt = "Customer: Ahmed, ID: 12345, Phone: 01011223344"
            await unified.generate_response(sensitive_prompt)

            # Check logs
            for record in caplog.records:
                log_msg = record.getMessage()
                # Forbidden items in logs
                forbidden = ["Ahmed", "12345", "01011223344"]
                for item in forbidden:
                    assert item not in log_msg, f"PII LEAK DETECTED: Log contains '{item}'"

    def test_smart_router_agent_heuristics(self):
        """
        Ensure SmartRouterAgent correctly classifies strategies in < 50ms
        and maintains modular integrity.
        """
        from backend.ai_agents.smart_router_agent import SmartRouterAgent

        router = SmartRouterAgent()

        # Test 1: Complex Problem Solving
        start = time.perf_counter()
        strategy_solve = router.determine_strategy(
            "Can you calculate the probability of this event? حلل البيانات"
        )
        end = time.perf_counter()
        latency_solve = (end - start) * 1000

        assert strategy_solve["task_type"] == "complex_problem_solving"
        assert strategy_solve["max_tokens"] >= 2048  # Should be higher for complex tasks
        assert latency_solve < 50, "Heuristic classification exceeded 50ms latency"

        # Test 2: Extraction
        strategy_extract = router.determine_strategy("استخرج جميع الأرقام من هذا النص")
        assert strategy_extract["task_type"] == "extraction"

        # Test 3: Fallback/Chat
        strategy_chat = router.determine_strategy("مرحبا ياسمين كيف حالك؟")
        assert strategy_chat["task_type"] == "customer_chat"
        assert "claude" in strategy_chat["alternatives"]

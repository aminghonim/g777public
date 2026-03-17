
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.ai_engine import AIEngine

async def test_router_logic():
    print("🚀 Testing Smart Task Router Logic...")
    engine = AIEngine()
    
    # 1. Test Intent Analysis Routing
    model = engine.get_model_for_task("intent_analysis")
    print(f"Task: intent_analysis -> Selected Model: {model}")
    assert model == "gemini-3-flash-preview", f"Expected gemini-3-flash-preview, got {model}"

    # 2. Test Computer Use Routing
    model = engine.get_model_for_task("computer_use")
    print(f"Task: computer_use -> Selected Model: {model}")
    assert model == "gemini-2.5-computer-use-preview", f"Expected gemini-2.5-computer-use-preview, got {model}"

    # 3. Test Unknown Task (Fallback)
    model = engine.get_model_for_task("unknown_task")
    print(f"Task: unknown_task -> Selected Model: {model}")
    assert model == "gemini-2.0-flash", f"Expected gemini-2.0-flash, got {model}"

    print("✅ Logic Check Passed!")

async def test_live_intent():
    print("\n📡 Testing Live Intent Analysis with Gemini 3.1 Flash...")
    engine = AIEngine()
    try:
        result = await engine.analyze_intent("بكم سعر الرحلة إلى دبي؟")
        print(f"Result: {result}")
        assert "intent" in result, "Result should contain 'intent'"
        print("✅ Live API Check Passed!")
    except Exception as e:
        print(f"❌ Live API Check Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_router_logic())
    # Note: Live test depends on API key validity
    asyncio.run(test_live_intent())

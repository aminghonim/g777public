import asyncio
import os
import logging
from dotenv import load_dotenv

# Ensure backend can be imported
import sys

sys.path.append(os.getcwd())

from backend.ai_engine import ai_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CNS_Verifier")


async def test_cns_pipeline():
    print("\n--- Starting CNS Pipeline Verification ---\n")

    # 1. Check if Orchestrator is initialized
    if not hasattr(ai_engine, "orchestrator"):
        print("FAIL: Orchestrator not found in AIEngine.")
        return

    print("PASS: Orchestrator initialized.")

    # 2. Simulate User Message
    user_message = "Hello Yasmine, what is the system status?"
    customer_phone = "test_user_001"

    print(f"\nSimulating Message: '{user_message}'")

    try:
        response = await ai_engine.generate_response(user_message, customer_phone)
        print(f"\nCNS Response:\n{response}")

        # 3. Verify Safety Gate (Simulated)
        # Since we can't easily force the LLM to write bad code in one turn,
        # we will manually invoke the safety check to prove integration.
        print("\n--- Testing Safety Gate Integration ---")
        from backend.core.safety import safety_protocol

        unsafe_code = "import os; os.system('rm -rf /')"
        is_valid, msg = safety_protocol.validate_code_safety(unsafe_code, "python")

        if not is_valid:
            print(f"PASS: Safety Protocol blocked unsafe code. Reason: {msg}")
        else:
            print("FAIL: Safety Protocol allowed unsafe code!")

        if response:
            print("\nPASS: Received response from CNS.")
        else:
            print("\nFAIL: Received empty response.")

    except Exception as e:
        print(f"\nFAIL: Error during generation: {e}")


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(test_cns_pipeline())

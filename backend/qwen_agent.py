import os
import sys
import asyncio
import logging
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai_client import UnifiedAIClient
from backend.mcp_manager import mcp_manager
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("qwen-bridge")

SAAF_RULES = """
You are acting as the CNS Squad local Qwen agent.
You MUST follow the SAAF IRON RULES:
1. The MCP tool call to agent-router has already been executed for you. Use the routing results to determine which specialist agent to invoke.
2. If tools are not available, explain that you are in 'restricted mode'.
3. Always prefix your internal thought process with [THOUGHT] and your response with [RESPONSE].
"""

async def run_qwen_agent(prompt: str):
    """Bridge Ollama/Gemini to SAAF Ecosystem via real MCP tool invocation."""

    logger.info("--- [CNS SQUAD QWEN BRIDGE] ---")

    # Step 1: Call MCP tool programmatically to find the best agent
    logger.info("Calling agent-router/find_best_agent via MCP protocol...")
    try:
        routing_result = await mcp_manager.call_tool(
            "agent-router__find_best_agent",
            {"task": prompt}
        )
        logger.info("MCP Tool call successful!")
        logger.info("Routing Result:\n%s", routing_result)
    except Exception as e:
        routing_result = f"⚠️ MCP Tool call failed: {str(e)}\nProceeding with default behavior."
        logger.warning(routing_result)

    # Step 2: Build enhanced prompt with routing results
    enhanced_prompt = f"""
TASK: {prompt}

MCP AGENT ROUTING RESULTS:
{routing_result}

Based on the routing results above, respond to the user's task appropriately.
If a specific agent was recommended, acknowledge it and proceed with the task using that agent's expertise.
"""

    # Step 3: Initialize AI client (prefer Ollama/Qwen, fallback to Gemini)
    client = UnifiedAIClient(provider="ollama", model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))

    if client.primary != "ollama":
        logger.warning("Ollama not detected. Using primary provider: %s", client.primary.upper())

    logger.info("Model: %s", client.primary.upper())
    logger.info("Processing request with MCP-enhanced context...")

    try:
        response = await client.generate_response(
            prompt=enhanced_prompt,
            system_message=SAAF_RULES
        )

        logger.info("--- [MODEL OUTPUT] ---")
        logger.info(response)
        logger.info("-------------------------")

    except Exception as e:
        logger.error("Error: %s", str(e))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.info("Usage: python3 backend/qwen_agent.py \"Your task here\"")
        sys.exit(1)

    user_prompt = sys.argv[1]
    asyncio.run(run_qwen_agent(user_prompt))

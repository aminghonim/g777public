import asyncio
import logging
from backend.ai_engine import AIEngine

logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)

async def test_mcp_discovery():
    logger.info("--- Discovery Test ---")
    engine = AIEngine()
    from backend.mcp_manager import mcp_manager

    tools = await mcp_manager.get_tools()
    logger.info(f"Found {len(tools)} tools from MCP servers.")
    for tool in tools:
        for func in tool.function_declarations:
            logger.info(f" - Tool: {func.name}")


async def test_ai_tool_use():
    logger.info("\n--- AI Tool-Use Test ---")
    engine = AIEngine()
    # Mocking a request that would trigger calendar tool
    message = "احجزي لي موعد بكرة الساعة 5 مساءً"
    logger.info(f"User Message: {message}")
    response = await engine.generate_response(message, "201012345678")
    logger.info(f"AI Response: {response}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(test_mcp_discovery())
    # Note: AI Tool-Use test might fail if Google Calendar requires auth,
    # but it will prove the loop works if it attempts to call the tool.
    # asyncio.run(test_ai_tool_use())

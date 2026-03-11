"""
Utility script to verify Model Context Protocol (MCP) server discovery and tool usage.
"""
import asyncio
import logging
from backend.ai_engine import AIEngine

logging.basicConfig(level=logging.INFO)


async def test_mcp_discovery():
    """Test the discovery of tools from configured MCP servers."""
    print("--- Discovery Test ---")
    from backend.mcp_manager import mcp_manager

    tools = await mcp_manager.get_tools_definitions()
    print(f"Found {len(tools)} tools from MCP servers.")
    for tool in tools:
        for func in tool.function_declarations:
            print(f" - Tool: {func.name}")


async def test_ai_tool_use():
    """Test the AI engine's ability to use discovery tools in a conversation."""
    print("\n--- AI Tool-Use Test ---")
    engine = AIEngine()
    # Mocking a request that would trigger calendar tool
    message = "احجزي لي موعد بكرة الساعة 5 مساءً"
    print(f"User Message: {message}")
    response = await engine.generate_response(message, "201012345678")
    print(f"AI Response: {response}")


if __name__ == "__main__":
    asyncio.run(test_mcp_discovery())
    # Note: AI Tool-Use test might fail if Google Calendar requires auth,
    # but it will prove the loop works if it attempts to call the tool.
    # asyncio.run(test_ai_tool_use())

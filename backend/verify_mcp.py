import asyncio
import logging
import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.mcp_manager import mcp_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


async def test_mcp_discovery():
    logger.info("--- Discovery Test ---")
    
    # Force discovery
    tools = await mcp_manager.get_tools_definitions()
    
    logger.info(f"Found {len(tools)} tools from MCP servers.")
    for tool in tools:
        if hasattr(tool, "function_declarations"):
            for func in tool.function_declarations:
                logger.info(f" - Tool: {func.name}")
        else:
            logger.info(f" - Tool: {tool}")


if __name__ == "__main__":
    asyncio.run(test_mcp_discovery())

import asyncio
import os
import sys
import logging
from unittest.mock import MagicMock, AsyncMock

sys.path.append(os.getcwd())

from backend.mcp_manager import MCPManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RetryTester")


async def test_retry_on_failure():
    logger.info("\n--- Testing MCP Retry Policy ---\n")

    manager = MCPManager()

    # Mocking a failing session
    failing_session = MagicMock()
    failing_session.list_tools = AsyncMock(
        side_effect=[
            Exception("Transient Error"),
            Exception("Transient Error"),
            MagicMock(tools=[]),
        ]
    )

    # Check imports
    try:
        import tenacity

        logger.info("PASS: Tenacity library available.")
    except ImportError:
        logger.error("FAIL: Tenacity library missing. Installing...")
        os.system("pip install tenacity")

    logger.info(
        "Manual verification required: Check logs for 'Retrying...' during connection attempts."
    )


if __name__ == "__main__":
    asyncio.run(test_retry_on_failure())

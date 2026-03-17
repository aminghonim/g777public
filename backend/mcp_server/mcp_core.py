import sys
import os
import asyncio
from typing import Optional

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from mcp.server.fastmcp import FastMCP
from backend.wa_gateway import WAGateway

# Initialize MCP Server
mcp = FastMCP("antigravity-core")


@mcp.tool()
async def send_whatsapp_message(phone: str, message: str) -> str:
    """
    Send a WhatsApp message via G777 System.
    """
    try:
        service = WAGateway()
        success, response = service.send_whatsapp_message(phone, message)
        return f"Status: {'Success' if success else 'Failed'}\nResponse: {response}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def check_system_status() -> str:
    """
    Check connection status and instance info.
    """
    try:
        service = WAGateway()
        is_connected = service._verify_connection()
        return f"Status: {'Connected' if is_connected else 'Disconnected'}\nInstance: {service.instance_name}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def get_system_logs(lines: int = 20) -> str:
    """
    Read last N lines from the diagnostic logs.
    """
    log_path = os.path.join(project_root, "webhook_incoming.log")
    if not os.path.exists(log_path):
        return "Log file not found."
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.readlines()
            return "".join(content[-lines:])
    except (IOError, OSError) as e:
        return f"Error reading logs: {str(e)}"


if __name__ == "__main__":
    mcp.run()

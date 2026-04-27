import sys
import os
import asyncio
from mcp.server.fastmcp import FastMCP

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.browser_core import WhatsAppBrowser

# Initialize MCP Server
mcp = FastMCP("chrome-devtools")


@mcp.tool()
async def open_whatsapp_web() -> str:
    """
    Launch Chrome and open WhatsApp Web (persistent session).
    """
    try:
        browser = WhatsAppBrowser(headless=False)
        # We start it but don't close it so it stays open for the user
        success = browser.load_whatsapp(login_timeout=60)
        return (
            "WhatsApp Web launched and ready."
            if success
            else "Launched but login check timed out."
        )
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def take_screenshot(name: str = "mcp_snapshot.png") -> str:
    """
    Take a screenshot of the current browser page.
    """
    try:
        browser = WhatsAppBrowser()
        # Connect to existing driver if possible
        browser.initialize_driver()
        path = browser.take_screenshot(name)
        return f"Screenshot saved to: {path}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def check_login_status() -> str:
    """
    Check if WhatsApp is currently logged in.
    """
    try:
        browser = WhatsAppBrowser()
        browser.initialize_driver()
        logged_in = browser.is_logged_in()
        return "Logged In" if logged_in else "Not Logged In"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()

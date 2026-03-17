import sys
import os
import asyncio
from typing import Optional

# إضافة المسار الجذري للمشروع لاستيراد مكتبات backend
# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

from mcp.server.fastmcp import FastMCP
from backend.wa_gateway import WAGateway

# تهيئة خادم MCP
# Initialize MCP Server
mcp = FastMCP("Antigravity G777")

@mcp.tool()
async def send_whatsapp_message(phone: str, message: str) -> str:
    """
    Send a WhatsApp message to a specific phone number using the G777 System.
    
    Args:
        phone: The phone number including country code (e.g., 201xxxxxxx)
        message: The text message to send
    """
    try:
        service = WAGateway()
        # محاولة الإرسال باستخدام بوابة واتساب
        success, response = service.send_whatsapp_message(phone, message)
        
        if success:
            return f" Message sent successfully to {phone}\nResponse: {response}"
        else:
            return f" Failed to send message to {phone}\nError: {response}"
            
    except Exception as e:
        return f" Internal Error: {str(e)}"

@mcp.tool()
async def check_system_status() -> str:
    """
    Check the connection status of the WhatsApp service.
    """
    try:
        service = WAGateway()
        is_connected = service._verify_connection()
        status = "Connected " if is_connected else "Disconnected "
        return f"System Status: {status}\nInstance: {service.instance_name}"
    except Exception as e:
        return f"Error checking status: {str(e)}"

@mcp.tool()
async def get_recent_logs(count: int = 10) -> str:
    """
    Get the most recent system logs (placeholder for now).
    """
    return "Logs functionality not fully linked to database yet."

if __name__ == "__main__":
    # تشغيل الخادم
    print(f" Starting Antigravity MCP Server...", file=sys.stderr)
    mcp.run()


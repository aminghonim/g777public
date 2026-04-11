import sys
import os
import asyncio
import logging
import subprocess
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("mcp-antigravity")

# إضافة المسار الجذري للمشروع لاستيراد مكتبات backend
# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

from mcp.server.fastmcp import FastMCP
from backend.cloud_service import AzureCloudService

# تهيئة خادم MCP
# Initialize MCP Server
mcp = FastMCP("Antigravity G777")

@mcp.tool()
async def send_whatsapp_message(phone: str, message: str) -> str:
    """
    Send a WhatsApp message to a specific phone number using the G777 Cloud System.
    
    Args:
        phone: The phone number including country code (e.g., 201xxxxxxx)
        message: The text message to send
    """
    try:
        service = AzureCloudService()
        # محاولة الإرسال باستخدام الخدمة السحابية
        success, response = service._send_evolution_text(phone, message)
        
        if success:
            return f" Message sent successfully to {phone}\nResponse: {response}"
        else:
            return f" Failed to send message to {phone}\nError: {response}"
            
    except Exception as e:
        return f" Internal Error: {str(e)}"

@mcp.tool()
async def check_system_status() -> str:
    """
    Check the connection status of the WhatsApp cloud service.
    """
    try:
        service = AzureCloudService()
        is_connected = service._verify_connection()
        status = "Connected " if is_connected else "Disconnected "
        return f"System Status: {status}\nInstance: {service.instance_name}"
    except Exception as e:
        return f"Error checking status: {str(e)}"

@mcp.tool()
async def save_and_verify_ui_code(filepath: str, code: str) -> str:
    """
    SAAF Integration: يحفظ الكود ويقوم بفحصه فوراً باستخدام أدوات فلاتر.
    """
    # 1. الحفظ الفعلي
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
    except Exception as e:
        return f"❌ Error saving file: {str(e)}"
    
    # 2. الرقابة المدمجة (SAAF Post-Hook)
    if filepath.endswith('.dart'):
        try:
            # تحديد المسار الجذري لمشروع فلاتر (الذي يحتوي على pubspec.yaml)
            flutter_project_dir = os.path.join(project_root, 'frontend_flutter')
            
            result = subprocess.run(
                ["flutter", "analyze", filepath], 
                cwd=flutter_project_dir,
                capture_output=True, 
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                # الكود فيه أخطاء
                error_msg = f"❌ SAAF UI GOVERNANCE BLOCKED:\nSyntax or static analysis errors found in {filepath}.\n\nAnalyzer Output:\n{result.stdout}\n\nFIX THESE ERRORS before proceeding."
                return error_msg
                
        except FileNotFoundError:
            return f"✅ Code saved to {filepath}, but skipped SAAF analysis (Flutter SDK not found)."
        except Exception as e:
            return f"✅ Code saved to {filepath}, but SAAF analysis failed: {str(e)}"

    return f"✅ Code saved and passed SAAF UI governance: {filepath}"


@mcp.tool()
async def get_recent_logs(count: int = 10) -> str:
    """
    Get the most recent system logs (placeholder for now).
    """
    return "Logs functionality not fully linked to database yet."

if __name__ == "__main__":
    # تشغيل الخادم
    logger.info("Starting Antigravity MCP Server...")
    mcp.run()


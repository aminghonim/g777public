
import asyncio
import random
from typing import List, Dict, Optional, Callable
from backend.warmer import AccountWarmer
from backend.cloud_service import cloud_service

class AccountWarmerController:
    """
    Controller for Account Warmer UI.
    Handles the warming loop, log management, and AI message generation.
    """
    def __init__(self):
        self.state = {
            'is_running': False,
            'logs': [],
            'current_count': 0,
            'total_count': 0
        }
        self.warmer = AccountWarmer()

    async def start_warming(self, 
                          phone1: str, 
                          phone2: str, 
                          count: int, 
                          delay: int, 
                          log_callback: Optional[Callable] = None):
        """Starts the warming loop between two accounts."""
        if self.state['is_running']:
            return

        self.state['is_running'] = True
        self.state['total_count'] = count
        self.state['current_count'] = 0
        self.state['logs'] = ["Warmer started..."]
        
        if log_callback: log_callback(self.state['logs'][-1])

        try:
            for i in range(count):
                if not self.state['is_running']: break
                
                self.state['current_count'] = i + 1
                
                # Generate AI Message
                msg = await self.warmer.generate_human_like_message()
                log_entry = f"[{i+1}/{count}] Sending: {msg}"
                self.state['logs'].append(log_entry)
                if log_callback: log_callback(log_entry)
                
                # Alternate between accounts or use provided targets
                target = phone1 if (i % 2 == 0) else phone2
                if target:
                    success, resp = await asyncio.to_thread(cloud_service.send_whatsapp_message, target, msg)
                    status = "✅ Success" if success else "❌ Failed"
                    res_log = f"Result: {status}"
                    self.state['logs'].append(res_log)
                    if log_callback: log_callback(res_log)
                else:
                    self.state['logs'].append("Skipping: No target phone.")
                    if log_callback: log_callback("Skipping: No target phone.")
                
                # Wait
                if i < count - 1:
                    actual_delay = delay + random.randint(-5, 5) # Add slight jitter
                    await asyncio.sleep(max(1, actual_delay))
                    
            self.state['logs'].append("Warming cycle completed.")
            if log_callback: log_callback("Warming cycle completed.")
        except Exception as e:
            err_log = f"Error in warming: {e}"
            self.state['logs'].append(err_log)
            if log_callback: log_callback(err_log)
        finally:
            self.state['is_running'] = False

    def stop_warming(self):
        self.state['is_running'] = False
        self.state['logs'].append("Stop requested by user.")

    def get_logs(self) -> str:
        return "\n".join(self.state['logs'])

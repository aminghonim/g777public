
from typing import Dict
from backend.cloud_service import cloud_service

class AutomationHubController:
    """
    Controller for Automation Hub.
    Manages high-level stats and coordination.
    """
    def __init__(self):
        self.state = {
            'instance_status': 'Unknown',
            'is_connected': False
        }

    def get_instance_info(self) -> Dict:
        """Returns connection status and instance metadata."""
        is_con = cloud_service.is_connected
        self.state['is_connected'] = is_con
        self.state['instance_status'] = 'Connected' if is_con else 'Disconnected'
        
        return {
            'status': self.state['instance_status'],
            'name': cloud_service.instance_name,
            'is_connected': is_con
        }

    def get_stats(self) -> Dict:
        """Returns dummy/mock stats for the dashboard."""
        return {
            'active_campaigns': 3,
            'engagement_rate': 'High',
            'ai_model': 'Gemini 2.0 Flash'
        }

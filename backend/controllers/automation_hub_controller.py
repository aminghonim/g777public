"""
Automation Hub Controller - Pure Backend Logic.
Manages instance status monitoring and system stats.
"""

import logging
from typing import Dict, Any
from backend.wa_gateway import wa_gateway

# CNS Logging Compliance
logger = logging.getLogger(__name__)

class AutomationHubController:
    """Handles high-level instance and system telemetry."""

    def get_instance_info(self) -> Dict[str, Any]:
        """Fetch instance connection status and metadata from gateway."""
        try:
            state = wa_gateway.get_connection_state()
            logger.debug(f"Automation Hub: Instance state is {state.get('instance', {}).get('state')}")
            return state
        except (ConnectionError, TimeoutError, RuntimeError) as e:
            logger.error(f"Automation Hub Error: Connectivity or Runtime issue: {e}")
            return {"instance": {"state": "error"}, "error": str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """Fetch high-level automation statistics."""
        return {
            "active_campaigns": 0,
            "total_messages_sent": 0,
            "is_connected": wa_gateway.is_connected
        }

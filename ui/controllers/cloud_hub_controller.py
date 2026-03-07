"""
Backward-compatibility shim for cloud_hub_controller module.
All logic has been moved to ui.controllers.wa_hub_controller.
"""

from ui.controllers.wa_hub_controller import WAHubController

# Legacy alias
CloudHubController = WAHubController

__all__ = ["WAHubController", "CloudHubController"]

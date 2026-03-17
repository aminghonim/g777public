
import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ModelRouter:
    """
    Centralized router for dynamic AI model selection based on task type.
    Follows CNS Squad Directive: Config-First & Modular Integrity.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "config.yaml"
        )
        self.routing_config = self._load_routing_config()

    def _load_routing_config(self) -> Dict[str, Any]:
        """Load model routing configuration from config.yaml"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Config file not found at {self.config_path}. Using hardcoded fallbacks.")
                return {}
                
            with open(self.config_path, "r", encoding="utf-8") as f:
                full_config = yaml.safe_load(f)
                return full_config.get("model_routing", {})
        except Exception as e:
            logger.error(f"Could not load model_routing from config.yaml: {e}")
            return {}

    def get_model_for_task(self, task: str, db_override: Optional[str] = None) -> str:
        """
        Dynamically routes to the best model based on task type.
        
        Args:
            task: The task identifier (e.g., 'intent_analysis', 'customer_chat').
            db_override: Optional model name from database (Highest priority).
            
        Returns:
            The model name to use.
        """
        # 1. DB Override (Tenant-specific)
        if db_override:
            return db_override

        # 2. Task-specific routing from config
        task_model = self.routing_config.get("tasks", {}).get(task)
        if task_model:
            return task_model

        # 3. Fallback to default in config
        default_model = self.routing_config.get("default")
        if default_model:
            return default_model

        # 4. Final Hardcoded Fallback (Absolute safety)
        return "gemini-2.0-flash"

# Global instance for easy access
model_router = ModelRouter()

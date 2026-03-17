"""
Smart Router Agent - Determines the optimal AI model and strategy for each request.

Wraps the core ModelRouter in an ADK-compatible interface while maintaining
Modular Integrity by not leaking routing logic into the AI Engine directly.
"""
# Standard library
import logging
from typing import Dict, Any, List, Optional

# Third-party
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from google import adk
    ADK_AVAILABLE = True
except ImportError:
    adk = None
    ADK_AVAILABLE = False

# Local / first-party
from backend.core.model_router import model_router

logger = logging.getLogger(__name__)

# Base class switches based on ADK availability to avoid import errors
_AgentBase = adk.Agent if ADK_AVAILABLE and adk else object


class SmartRouterAgent(_AgentBase):
    """
    ADK-compliant Agent for determining the optimal AI routing strategy.
    Encapsulates `model_router` to maintain Modular Integrity.
    Falls back to a plain object when google-adk is not installed.
    """

    def __init__(self, tools: Optional[List[Any]] = None):
        instruction = self._build_instructions()

        if ADK_AVAILABLE and adk is not None:
            # ADK requires name to be a valid Python identifier
            super().__init__(
                name="SmartRouter",
                instruction=instruction,
                tools=tools or []
            )
        logger.info("SmartRouterAgent initialized. ADK available: %s", ADK_AVAILABLE)

    @staticmethod
    def _build_instructions() -> str:
        """Constructs the system instructions for the router agent."""
        return """
ROLE: Smart Task Router (AI Engine Traffic Controller)
TASK: Analyze incoming user requests and determine the optimal routing strategy.

AVAILABLE TASK TYPES:
1. intent_analysis: Fast, reliable classification.
2. customer_chat: General conversation, balance of speed and intelligence.
3. extraction: Extracting structured data from text.
4. complex_problem_solving: High reasoning requirements, multi-step logic.
5. computer_use: Specialized vision or browser control.
6. content_generation: Image or complex document generation.
7. market_research: Deep information gathering and web searching.

OUTPUT FORMAT:
You must output a JSON object ONLY, with the following schema:
{
    "task_type": "string (from available list)",
    "confidence": "float (0.0 to 1.0)",
    "reasoning": "string (brief explanation why this task type was chosen)"
}
"""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def determine_strategy(self, message: str, db_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Determines the optimal execution strategy for a given message.

        Args:
            message: The user's input/request.
            db_override: Optional tenant-level override for the model.

        Returns:
            Dictionary containing the routing strategy (model, provider, tokens, alternatives).
        """
        # Determine Task Type (Heuristic for speed to ensure < 50ms latency)
        task_type = self._fast_task_classification(message)

        # Get Model from core ModelRouter (Modular Integrity)
        model_name = model_router.get_model_for_task(task_type, db_override=db_override)

        # Enrich Strategy (Provider, Tokens, Fallbacks)
        strategy = self._enrich_strategy(model_name, task_type)

        logger.info("Routing Strategy Determined: Task='%s', Model='%s'", task_type, model_name)
        return strategy

    def _fast_task_classification(self, message: str) -> str:
        """Heuristic-based fast classification to save AI tokens & latency."""
        msg_lower = message.lower()
        if any(kw in msg_lower for kw in ["search", "find", "research", "look up", "ابحث"]):
            return "market_research"
        elif any(kw in msg_lower for kw in ["extract", "parse", "get the email", "استخرج"]):
            return "extraction"
        elif any(kw in msg_lower for kw in ["solve", "calculate", "analyze", "احسب", "حلل"]):
            return "complex_problem_solving"
        elif any(kw in msg_lower for kw in ["image", "generate", "draw", "ارسم", "صورة"]):
            return "content_generation"
        elif any(kw in msg_lower for kw in ["click", "browser", "computer", "شاشة", "متصفح"]):
            return "computer_use"

        # Default to customer_chat for standard conversational inputs
        return "customer_chat"

    def _enrich_strategy(self, model_name: str, task_type: str) -> Dict[str, Any]:
        """Adds provider, token limits, and fallbacks based on the model."""
        
        # Determine provider based on model name prefix/content
        model_lower = model_name.lower()
        if "gpt" in model_lower:
            provider = "openai"
        elif "claude" in model_lower:
            provider = "anthropic"
        elif "azure" in model_lower:
            provider = "azure"
        else:
            provider = "gemini"

        strategy: Dict[str, Any] = {
            "task_type": task_type,
            "primary_model": model_name,
            "provider": provider,
            "max_tokens": 1024,
            "alternatives": ["claude"]
        }

        # Specific model overrides
        if "pro" in model_name:
            strategy["max_tokens"] = 8192
            # Prefer Claude as fallback for complex reasoning tasks
            strategy["alternatives"] = ["claude"]
        elif "lite" in model_name or "flash" in model_name:
            strategy["max_tokens"] = 2048
            strategy["alternatives"] = ["claude"]

        return strategy

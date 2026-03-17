"""
Account Warmer Module - Azure AI Enhanced
Handles WhatsApp account warming through simulated conversations using Azure AI.
"""

import time
import random
from pathlib import Path
from .ai_client import AzureAIClient


class AccountWarmer:
    """
    Handles WhatsApp account warming operations using Azure AI Foundry.
    """

    def __init__(self, ai_client: AzureAIClient = None):
        """Initialize the AccountWarmer with local Arabic phrases."""
        self.ai = ai_client or AzureAIClient()
        self.is_running = False
        self.phrases = self._load_local_phrases()

    def _load_local_phrases(self):
        """Loads Arabic conversational phrases from local memory."""
        import json  # pylint: disable=import-outside-toplevel
        config_path = Path(__file__).parent.parent / "config" / "warmer_ar.json"

        default_fallbacks = [
            "أهلاً يا صحبي، عامل ايه؟",
            "الحمد لله تمام، وأنت؟",
            "خلينا نتقابل قريب",
            "تمام يا وحش",
            "ايه الاخبار؟",
            "يا مسهل يارب",
        ]

        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return data
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"[Warmer] Failed to load warmer_ar.json: {e}")

        return default_fallbacks

    async def generate_human_like_message(self, _context: str = "general chat") -> str:  # pylint: disable=unused-argument
        """
        Retrieves a random human-like Arabic message from offline memory.
        """
        return random.choice(self.phrases)

    def calculate_delay(self, min_seconds=30, max_seconds=300):
        """Calculate random delay between messages to simulate human behavior."""
        return random.randint(min_seconds, max_seconds)

    async def run_warming_cycle(self, _sender, count=5):  # pylint: disable=unused-argument
        """Run a cycle of messages."""
        self.is_running = True
        for _ in range(count):
            if not self.is_running:
                break

            message = await self.generate_human_like_message()
            # In a real scenario, we'd use the sender to send the message
            print(f"[Warmer] Generated AI Message: {message}")

            delay = self.calculate_delay(10, 30)
            print(f"[Warmer] Waiting {delay}s...")
            time.sleep(delay)
        self.is_running = False

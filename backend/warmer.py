"""
Account Warmer Module - Azure AI Enhanced
Handles WhatsApp account warming through simulated conversations using Azure AI.
"""

import time
import random
import logging
from pathlib import Path
from .ai_client import AzureAIClient

logger = logging.getLogger(__name__)

class AccountWarmer:
    """
    Handles WhatsApp account warming operations using Azure AI Foundry.
    """
    
    def __init__(self, ai_client: AzureAIClient = None):
        """Initialize the AccountWarmer with Azure AI Client."""
        self.ai = ai_client or AzureAIClient()
        self.is_running = False
    
    async def generate_human_like_message(self, context: str = "general chat") -> str:
        """
        Generate a random human-like message for warming using Azure AI.
        """
        system_prompt = (
            "You are a helpful assistant helping to warm up a WhatsApp account. "
            "Generate a Short, natural sounding Arabic message for a casual conversation between two friends. "
            "The message should be brief (max 10 words) and use Egyptian slang (Ammiya). "
            "Do not include emojis except one or two natural ones."
        )
        
        prompt = f"Context: {context}. Give me one casual message to send."
        
        try:
            message = await self.ai.generate_response(prompt, system_prompt)
            return message.strip().strip('"')
        except Exception as e:
            # Fallback for offline or errors
            fallbacks = ["أهلاً يا صحبي، عامل ايه؟", "الحمد لله تمام، وأنت؟", "خلينا نتقابل قريب", "تمام يا وحش"]
            return random.choice(fallbacks)
    
    def calculate_delay(self, min_seconds=30, max_seconds=300):
        """Calculate random delay between messages to simulate human behavior."""
        return random.randint(min_seconds, max_seconds)
    
    async def run_warming_cycle(self, sender, count=5):
        """Run a cycle of messages."""
        self.is_running = True
        for i in range(count):
            if not self.is_running: break
            
            message = await self.generate_human_like_message()
            # In a real scenario, we'd use the sender to send the message
            logger.info(f"[Warmer] Generated AI Message: {message}")
            
            delay = self.calculate_delay(10, 30)
            logger.info(f"[Warmer] Waiting {delay}s...")
            time.sleep(delay)
        self.is_running = False

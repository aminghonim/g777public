"""
AI Service - Google Gemini Integration
======================================
Handles communication with Google's Gemini API for text generation and data extraction.
"""

import os
import aiohttp
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"


async def generate_ai_response(prompt, system_message=""):
    """
    Calls AI Client and returns both text and token usage.
    """
    try:
        from backend.ai_client import UnifiedAIClient

        client = UnifiedAIClient()
        response_data = await client.generate_response(prompt, system_message)

        # Normalize response: client may return a string or dict
        if isinstance(response_data, dict):
            text = response_data.get("text")
            usage = response_data.get("usage", {})
        else:
            text = response_data
            usage = {}

        # Log token usage for visibility
        print(
            f"[AI-USAGE] Prompt: {usage.get('prompt_tokens', 0)} | Completion: {usage.get('completion_tokens', 0)} | Total: {usage.get('total_tokens', 0)}"
        )

        return {"text": text, "usage": usage}
    except Exception as e:
        print(f"[ERROR] AI Service failure: {e}")
        return {"text": f"Error: {e}", "usage": {}}


# Legacy alias for direct text extraction if needed
async def call_gemini_direct(prompt):
    res = await generate_ai_response(prompt)
    return res.get("text")

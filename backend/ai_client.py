"""
Unified AI Client - Provides a resilient, multi-provider interface for AI generation.

Supports Gemini, Azure OpenAI, and Anthropic Claude with automatic fallback
so that a failure in any single provider does not halt response generation.
"""
import os
import logging
from typing import Optional

from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    genai = None

try:
    from openai import AsyncAzureOpenAI
except ImportError:
    AsyncAzureOpenAI = None

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

from backend.core.model_router import model_router

load_dotenv()
logger = logging.getLogger(__name__)


class GeminiAIClient:
    """
    Gemini 2.0 Flash Client - المجاني والأسرع
    يستخدم المكتبة الجديدة google.genai
    """

    def __init__(self, api_key: Optional[str] = None):
        if not genai:
            logger.warning("google-genai package not installed")
            self.client = None
            return

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set. Gemini client disabled.")
            self.client = None
            return

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_router.get_model_for_task("customer_chat")
        logger.info("Gemini Client initialized with model: %s", self.model_name)

    async def generate_response(self, prompt: str, system_message: str = "") -> str:
        """توليد رد باستخدام Gemini 2.0 Flash"""
        full_prompt = (
            f"{system_message}\n\nUser Question: {prompt}" if system_message else prompt
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_name, contents=full_prompt
        )

        # Token usage is available via response.usage_metadata but not consumed here.
        # Log or forward to a telemetry service when observability is wired up.
        return response.text

    def generate_response_sync(self, prompt: str, system_message: str = "") -> str:
        """نسخة متزامنة للاستخدام في Azure Functions"""
        full_prompt = (
            f"{system_message}\n\nUser Question: {prompt}" if system_message else prompt
        )

        response = self.client.models.generate_content(
            model=self.model_name, contents=full_prompt
        )
        return response.text


class AzureAIClient:
    """
    Azure OpenAI Client - للعمل الاحترافي والـ Stability
    """

    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = "2024-02-15-preview"
        self.client = None

        if not AsyncAzureOpenAI:
            logger.warning("openai package not installed")
            return

        if (
            not self.api_key
            or not self.endpoint
            or "your_" in self.api_key
            or self.api_key == "not_used"
        ):
            return

        try:
            self.client = AsyncAzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.endpoint,
                api_version=self.api_version,
            )
            logger.info("Azure OpenAI connected to: %s", self.endpoint)
        except Exception as e:
            logger.error("Failed to init Azure OpenAI: %s", e)

    async def generate_response(
        self, prompt: str, system_message: str = "You are a helpful assistant."
    ) -> str:
        """توليد رد باستخدام Azure OpenAI"""
        if not self.client:
            return "Error: Azure OpenAI is not configured."

        try:
            # Call the Azure client's chat completion API and extract content
            resp = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}]
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"


class ClaudeAIClient:
    """
    Anthropic Claude Client - للبدائل عالية الدقة
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if not AsyncAnthropic:
            logger.warning("anthropic package not installed")
            return

        if self.api_key:
            try:
                self.client = AsyncAnthropic(api_key=self.api_key)
                self.model_name = "claude-3-5-sonnet-20241022"
                logger.info("Claude Client initialized with model: %s", self.model_name)
            except Exception as e:
                logger.error("Failed to init Claude: %s", e)
        else:
            logger.warning("ANTHROPIC_API_KEY not set. Claude client disabled.")

    async def generate_response(self, prompt: str, system_message: str = "") -> str:
        """توليد رد باستخدام Claude"""
        if not self.client:
            return "Error: Claude is not configured."

        try:
            message = await self.client.messages.create(
                model=self.model_name,
                max_tokens=1024,
                system=system_message,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"


class UnifiedAIClient:
    """
    Unified Client - يختار تلقائياً بين Gemini و Azure
    """

    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None):
        self.gemini_client = None
        self.azure_client = None
        self.claude_client = None
        self.primary = None

        # 1. Attempt to initialize all clients for resilience
        try:
            self.gemini_client = GeminiAIClient(api_key=api_key if provider == "gemini" else None)
        except Exception as e:
            logger.debug("Gemini init failed: %s", e)

        try:
            self.claude_client = ClaudeAIClient(api_key=api_key if provider == "claude" else None)
        except Exception as e:
            logger.debug("Claude init failed: %s", e)

        try:
            self.azure_client = AzureAIClient()
        except Exception as e:
            logger.debug("Azure init failed: %s", e)

        # 2. Determine Primary (Requested -> Auto-detect)
        requested_client = None
        if provider == "gemini":
            requested_client = self.gemini_client
        elif provider == "claude":
            requested_client = self.claude_client
        elif provider == "azure":
            requested_client = self.azure_client

        if requested_client and getattr(requested_client, "client", None):
            self.primary = provider
        else:
            # Auto-detect priority
            if self.gemini_client and self.gemini_client.client:
                self.primary = "gemini"
            elif self.claude_client and self.claude_client.client:
                self.primary = "claude"
            elif self.azure_client and self.azure_client.client:
                self.primary = "azure"
            else:
                self.primary = None

        logger.info("Unified AI Client using: %s", self.primary)

    async def generate_response(self, prompt: str, system_message: str = "") -> str:
        """توليد رد مع fallback"""
        # Define prioritized providers
        providers = [
            ("gemini", self.gemini_client),
            ("claude", self.claude_client),
            ("azure", self.azure_client),
        ]

        # 1. Re-order based on primary selection
        ordered_providers = []
        if self.primary != "none":
            # Finding the primary in the list
            primary_tuple = next((p for p in providers if p[0] == self.primary), None)
            if primary_tuple:
                ordered_providers.append(primary_tuple)

            # Add others
            for p in providers:
                if p[0] != self.primary:
                    ordered_providers.append(p)
        else:
            ordered_providers = providers

        # 2. Execution Loop with Fallback
        last_error = None
        for name, client in ordered_providers:
            if client and getattr(client, "client", None):
                try:
                    return await client.generate_response(prompt, system_message)
                except Exception as e:
                    last_error = e
                    logger.warning("AI Provider %s failed: %s", name, e)
                    continue

        return f"Error: All AI providers failed. Last error: {str(last_error)}"

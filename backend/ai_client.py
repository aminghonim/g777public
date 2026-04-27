"""
Antigravity AI Client - Multi-Provider Support
يدعم: Google Gemini 2.0 (Free) + Azure OpenAI (Pro)
تم التحديث للمكتبة الجديدة google.genai
"""

import os
import logging
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiAIClient:
    """
    Gemini 2.0 Flash Client - المجاني والأسرع
    يستخدم المكتبة الجديدة google.genai
    """

    def __init__(self, api_key=None):
        from google import genai

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            # For testing, we might proceed if mocked, but generally warn/error
            pass

        # If API key is missing (and not mocked elsewhere/handled), client init might fail
        # But we'll try to initialize to allow mocking validation
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None  # Client needs key

        self.model_name = "gemini-2.5-flash"  # Latest model!
        logger.info(f"Gemini Client initialized with model: {self.model_name}")

    async def generate_response(self, prompt: str, system_message: str = "") -> str:
        """توليد رد باستخدام Gemini 2.0 Flash"""
        full_prompt = (
            f"{system_message}\n\nUser Question: {prompt}" if system_message else prompt
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_name, contents=full_prompt
        )

        usage = {
            "prompt_tokens": (
                response.usage_metadata.prompt_token_count
                if hasattr(response, "usage_metadata")
                else 0
            ),
            "completion_tokens": (
                response.usage_metadata.candidates_token_count
                if hasattr(response, "usage_metadata")
                else 0
            ),
            "total_tokens": (
                response.usage_metadata.total_token_count
                if hasattr(response, "usage_metadata")
                else 0
            ),
        }

        # Return text only (tests expect plain string). Usage is logged above.
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

        if (
            not self.api_key
            or not self.endpoint
            or "your_" in self.api_key
            or self.api_key == "not_used"
        ):
            # Silently skip if explicitly not used or missing
            pass
        else:
            try:
                from openai import AsyncAzureOpenAI

                self.client = AsyncAzureOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=self.endpoint,
                    api_version=self.api_version,
                )
                logger.info(f"Azure OpenAI connected to: {self.endpoint}")
            except ImportError:
                logger.warning("openai package not installed")

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


class OllamaAIClient:
    """
    Ollama AI Client - لتشغيل النماذج محلياً (مثل Qwen)
    تستخدم واجهة OpenAI المتوافقة في Ollama
    """

    def __init__(self, api_base=None, model_name=None):
        self.api_base = api_base or os.getenv("OLLAMA_API_BASE", "http://localhost:11434/v1")
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen:7b")
        self.timeout = httpx.Timeout(60.0, connect=10.0)
        logger.info(f"Ollama Client initialized: {self.model_name} at {self.api_base}")

    async def generate_response(self, prompt: str, system_message: str = "") -> str:
        """توليد رد باستخدام Ollama"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})

                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "temperature": 0.7,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama API Error: {e}")
            return f"Error connecting to local Qwen (Ollama): {str(e)}"


class UnifiedAIClient:
    """
    Unified Client - يختار تلقائياً بين Gemini و Azure و Ollama/Qwen
    """

    # Task-to-Model routing map — used by subsystems to resolve
    # the correct model for a given task type without hardcoding.
    TASK_MODEL_MAP = {
        "CHAT": os.getenv("CHAT_MODEL", "gemini-2.5-flash"),
        "INTENT_CLASSIFICATION": os.getenv("INTENT_MODEL", "gemini-2.5-flash"),
        "WEB_OPERATION": os.getenv("BROWSER_USE_MODEL", "gemini-2.0-flash"),
    }

    def __init__(self, provider=None, model=None, api_key=None):
        self.gemini_client = None
        self.azure_client = None
        self.ollama_client = None
        self.primary = None

        # Determine provider from model name if not explicit
        if not provider and model:
            if "qwen" in model.lower() or "ollama" in model.lower():
                provider = "ollama"
            elif "gemini" in model.lower():
                provider = "gemini"
            elif "gpt" in model.lower():
                provider = "azure"

        # If specific provider requested
        if provider == "gemini":
            try:
                self.gemini_client = GeminiAIClient(api_key=api_key)
                self.primary = "gemini"
            except Exception:
                pass
        elif provider == "azure":
            try:
                self.azure_client = AzureAIClient()
                if self.azure_client.client:
                    self.primary = "azure"
            except Exception:
                pass
        elif provider == "ollama" or provider == "qwen":
            try:
                self.ollama_client = OllamaAIClient(model_name=model)
                self.primary = "ollama"
            except Exception:
                pass

        # Auto-detection if no specific provider or init failed
        if not self.primary:
            # 1. Try Ollama if configured
            if os.getenv("OLLAMA_API_BASE"):
                try:
                    self.ollama_client = OllamaAIClient()
                    self.primary = "ollama"
                except Exception:
                    pass

            # 2. Try Gemini
            if not self.primary:
                try:
                    self.gemini_client = GeminiAIClient()
                    self.primary = "gemini"
                    logger.info("Gemini initialized as primary")
                except Exception as e:
                    logger.warning(f"Gemini init failed: {e}")

            # 3. Try Azure
            if not self.primary:
                try:
                    self.azure_client = AzureAIClient()
                    if self.azure_client.client:
                        self.primary = "azure"
                except Exception:
                    pass

        if not self.primary:
            logger.warning("No AI provider available during init!")

        logger.info(f"Unified AI Client using: {self.primary}")

    async def generate_response(self, prompt: str, system_message: str = "") -> str:
        """توليد رد مع fallback"""
        try:
            if self.primary == "gemini" and self.gemini_client:
                return await self.gemini_client.generate_response(
                    prompt, system_message
                )
            elif self.primary == "azure" and self.azure_client:
                return await self.azure_client.generate_response(prompt, system_message)
            elif self.primary == "ollama" and self.ollama_client:
                return await self.ollama_client.generate_response(prompt, system_message)
        except Exception as e:
            logger.warning(f"Primary {self.primary} failed: {e}")
            # Fallback chain: Gemini -> Azure -> Ollama
            for client in [self.gemini_client, self.azure_client, self.ollama_client]:
                if client and client != getattr(self, f"{self.primary}_client", None):
                    try:
                        return await client.generate_response(prompt, system_message)
                    except Exception:
                        continue

        return "Error: All AI providers failed."

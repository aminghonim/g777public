"""
G777 Intent Engine - Powered by Gemini 2.0 Flash (Modern SDK)
=============================================================
Handles AI logic for intent classification, entity extraction,
and dynamic response generation using the new google-genai SDK.
"""

import os
import json
import asyncio
import yaml
import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from .db_service import (
    get_tenant_settings,
    get_system_prompt,
    format_offerings_for_prompt,
    get_customer_by_phone,
    is_excluded,
    get_training_samples,
)
from .mcp_manager import mcp_manager
from backend.agents.orchestrator import Orchestrator
from google import adk
from backend.ai_agents.persona_agent import PersonaAgent
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIEngine:
    def __init__(self):
        self.strings = {}  # Safety initialization
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error(
                self._get_string(
                    "errors.missing_api_key", "WARNING: GEMINI_API_KEY not found!"
                )
            )

        # Initialize Client (Still used for lightweight tasks like intent analysis)
        self.client = genai.Client(api_key=self.api_key)

        # Initialize CNS Orchestrator
        self.orchestrator = Orchestrator()

        # Initialize ADK Persona Agent (Modernized)
        self.persona_agent = PersonaAgent()

        # Load AI Instructions
        self.instructions = self._load_instructions()

        # Load localized strings
        self.strings = self._load_strings()

    def _load_strings(self) -> Dict[str, Any]:
        """Load localized strings from JSON config"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "strings.json"
            )
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load strings.json: {e}")
            return {}

    def _get_string(self, key_path: str, default: str = "") -> str:
        """Helper to get nested strings from localization config"""
        keys = key_path.split(".")
        val = self.strings
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
        return val if isinstance(val, str) else default

    def _load_instructions(self) -> Dict[str, Any]:
        """Load AI instructions from YAML config"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "ai_instructions.yaml"
            )
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load AI instructions: {e}")
            return {}

    def _get_settings(self):
        return get_tenant_settings()

    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze if message is business-related and detect intent.
        Kept lightweight using direct client for speed.
        """
        settings = self._get_settings()
        model_name = settings.get("ai_model", "gemini-2.0-flash")

        # Get system instruction from config
        intent_config = self.instructions.get("intent_classifier", {})
        system_instruction = f"""{intent_config.get('role', 'Intent Classifier')}

TASK: {intent_config.get('task', 'Classify user intent')}

RULES:
{chr(10).join('- ' + rule for rule in intent_config.get('rules', []))}

EXAMPLE:
{intent_config.get('example', '')}

Now analyze this message:"""

        prompt = f'{system_instruction}\n\nMESSAGE: "{message}"\n\nYOUR JSON RESPONSE:'

        try:
            response = await self.client.aio.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,  # Deterministic for classification
                ),
            )

            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```json")[-1].split("```")[0].strip()

            return json.loads(text)
        except Exception as e:
            logger.error(f"AI Intent Error: {e}")
            return {"is_business": True, "intent": "unknown", "confidence": 0.0}

    async def extract_and_update_info(self, message: str, customer: Dict[str, Any]):
        """
        Extract missing info from message and update customer profile.
        """
        missing = customer.get("missing_fields", [])
        if not missing:
            return customer

        # Enhanced Prompt for Robust Extraction
        prompt = f"""
        SYSTEM: You are a strict Data Extraction Engine.
        TASK: Extract known missing entities from the User Message based on the Required Keys list.
        
        REQUIRED KEYS: {json.dumps(missing)}
        USER MESSAGE: "{message}"
        
        INSTRUCTIONS:
        1. Only extract values definitely present in the message.
        2. If a value is not found, do not include the key in the JSON.
        3. Return a clean JSON object. No markdown formatting (```json).
        4. Normalize names (e.g., "Ahmed" -> "Ahmed").
        
        EXAMPLE:
        Keys: ["name", "location"]
        Msg: "I am Omar from Dubai"
        Output: {{"name": "Omar", "location": "Dubai"}}
        
        OUTPUT JSON:
        """

        settings = self._get_settings()
        model_name = settings.get("ai_model", "gemini-2.0-flash-exp")

        try:
            response = await self.client.aio.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,  # Zero temp for deterministic extraction
                ),
            )
            # Clean possible markdown if model misbehaves
            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)

            if data and isinstance(data, dict):
                from .db_service import mark_field_collected, update_customer

                updates = {}
                # Update specific columns
                if "name" in data:
                    updates["name"] = data["name"]
                if "location" in data:
                    updates["location"] = data["location"]

                # Update custom_data
                custom_data = customer.get("custom_data", {}) or {}  # Ensure dict
                for k, v in data.items():
                    if k not in ["name", "location"]:
                        custom_data[k] = v
                        mark_field_collected(customer["phone"], k)

                if custom_data != customer.get("custom_data", {}):
                    updates["custom_data"] = custom_data

                # Apply DB updates
                if updates:
                    update_customer(customer["phone"], updates)

                    # Cleanup missing fields list locally
                    for k in data:
                        if k in missing:
                            mark_field_collected(customer["phone"], k)
                            if k in customer.get("missing_fields", []):
                                customer["missing_fields"].remove(k)

                    customer.update(updates)

        except Exception as e:
            logger.error(f"Extraction Error: {e}")

        return customer

    def _build_system_prompt(
        self,
        persona: Dict[str, Any],
        profile: Dict[str, Any],
        # trips_text and faq_text are now removed from strict signature or ignored
        customer_name: str,
        message: str,
        conversation_history: str,
    ) -> str:
        """
        Constructs a Lean System Prompt relying on Orchestrator's Context Injection.
        """

        # Core Identity
        system_prompt = f"""
You are {persona.get('name', 'Yasmine')}, {persona.get('role', 'AI Assistant')} at {profile.get('name', 'TripiGo')}.
Your Tone: {persona.get('tone', 'Helpful and Friendly')}.
Specialty: {profile.get('specialty', 'Travel')}.

RULES:
1. {persona.get('self_identification_rule', 'Never identify as AI.')}
2. Use the provided Context (Sensory & Memory) to answer.
3. If you don't know, admit it or ask for clarification.
4. Current Customer: {customer_name}
"""
        return system_prompt

    async def generate_response(
        self, message: str, customer_phone: str, conversation_history: str = ""
    ) -> str:
        """
        Main CNS Entry Point.
        Delegates to Orchestrator for full cognitive processing.
        """
        # 0. Check Exclusion
        if is_excluded(customer_phone):
            logger.info(f"Bot is PAUSED/EXCLUDED for {customer_phone}")
            return ""
        # 1. Load Data (Fallback Source)
        try:
            with open("trips_db.json", "r", encoding="utf-8") as f:
                db_data = json.load(f)
        except Exception as e:
            logger.error(f"DB Load Error: {e}")
            db_data = {}

        persona = db_data.get("ai_persona", {})
        profile = db_data.get("company_profile", {})

        # Prepare Fallback Context (Legacy Data)
        # We construct distinct text blocks just in case we need them as fallback
        trips = db_data.get("trips", [])
        trips_text = "\n".join(
            [
                f"- {t.get('type')}: {t.get('price')} ({', '.join(t.get('destinations', []))})"
                for t in trips
            ]
        )
        faq = db_data.get("faq", {})
        faq_text = "\n".join([f"Q: {k} A: {v}" for k, v in faq.items()])

        fallback_context = f"Available Trips:\n{trips_text}\n\nFAQs:\n{faq_text}"

        customer_name = "مجهول"  # Placeholder - in real app would resolve from DB

        # 2. Build Lean System Prompt
        system_prompt = self._build_system_prompt(
            persona,
            profile,
            customer_name,
            message,
            conversation_history,
        )

        # 3. Define Tools (MCP)
        # In the future, these will be strictly typed ADK tools.
        # For now, we pass them as definitions if the Orchestrator needs them
        # (Though Orchestrator currently loads its own context,
        # the gemini client needs the tools config passed in generate_content).

        # Current Orchestrator implementation handles tool definitions internally
        # or via mcp_manager. Here we strictly delegate.

        tools = await mcp_manager.get_tools_definitions()

        # 4. Delegate to Orchestrator or ADK Runner
        try:
            # Modern Track: ADK Runner
            try:
                # Refresh tools for the persona agent (Modernized via ADK)
                # We create a specific instance with tools for this run
                request_agent = PersonaAgent(tools=tools)
                runner = adk.Runner(agent=request_agent)
                response_text = ""

                # ADK executes the tool-use loop automatically
                async for event in runner.run_async(
                    user_id="g777_admin",
                    session_id=customer_phone,
                    new_message=types.Content(
                        role="user", parts=[types.Part(text=message)]
                    ),
                ):
                    if hasattr(event, "text") and event.text:
                        response_text += event.text

                if response_text:
                    return response_text

            except Exception as adk_err:
                logger.error(
                    f"ADK Execution Error: {adk_err}. Falling back to Orchestrator."
                )

            # Legacy/Safety Track: Orchestrator
            response_text = await self.orchestrator.process_request(
                message=message,
                system_prompt=system_prompt,
                tools=tools,
                conversation_history=conversation_history,
                fallback_context=fallback_context,
            )
            return response_text

        except Exception as e:
            logger.error(f"Generation Error: {e}", exc_info=True)
            return self._get_string("errors.ai_api_overload")

    def _load_kb(self) -> Optional[Dict[str, Any]]:
        """Surgically load knowledge base from JSON"""
        try:
            kb_path = os.path.join(os.path.dirname(__file__), "..", "trips_db.json")
            with open(kb_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load trips_db.json: {e}")
            return None

    def _format_trips(self, trips: list) -> str:
        """Format trip data for prompt"""
        text = self._get_string("persona.trips_header") + "\n"
        for t in trips:
            details = ", ".join(
                t.get("includes", []) + t.get("highlights", []) + t.get("extras", [])
            )
            text += f"- **{t.get('type')}**: السعر {t.get('price')} ({details})\n  الوجهات: {', '.join(t.get('destinations', []))}\n"
        return text

    async def summarize_customer(self, conversation_text: str) -> str:
        """Generate a summary of customer interests"""
        prompt_template = get_system_prompt("summary_generator")
        if not prompt_template:
            return ""

        prompt = prompt_template.replace("{conversation}", conversation_text)
        settings = self._get_settings()
        model_name = settings.get("ai_model", "gemini-2.0-flash-exp")

        try:
            response = await self.client.aio.models.generate_content(
                model=model_name, contents=prompt
            )
            return response.text.strip()
        except Exception:
            return ""


# Global Instance
ai_engine = AIEngine()

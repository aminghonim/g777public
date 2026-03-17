from google import genai
from google.genai import types
import logging
import os
import json
from typing import Dict, Any, List, Optional
from backend.mcp_manager import mcp_manager
from backend.agents.researcher import ResearcherAgent  # <--- SPECIALIST AGENTEGRATION
from backend.agents.coder import CoderAgent  # <--- SPECIALIST AGENT
from backend.agents.sentinel import SentinelAgent  # <--- SPECIALIST AGENT
from backend.core.safety import safety_protocol  # <--- SAFETY INTEGRATION
from backend.agents.skills.intent_alignment import (
    IntentAlignment,
)  # <--- SKILL INTEGRATION
from backend.memory.vector_store_manager import VectorStoreManager
from backend.observers.system_monitor import SystemMonitor
from backend.observers.file_watcher import CodeChangeHandler
from backend.executors.sandbox import SandboxExecutor
from backend.core.model_router import model_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Orchestrator:
    """
    The Central Nervous System Executive.
    Coordinates all other components: Memory, Senses, Actions, and Sub-Agents.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        # Priority: explicit arg -> router -> fallback
        self.model_name = model_name or model_router.get_model_for_task("customer_chat")

        if not self.api_key:
            logger.error("WARNING: GEMINI_API_KEY not found! Orchestrator may fail.")

        # Initialize Pillars
        self.memory = VectorStoreManager()
        self.sandbox = SandboxExecutor()
        self.system_monitor = SystemMonitor()
        self.client = genai.Client(api_key=self.api_key)
        self.researcher = ResearcherAgent(self)  # <--- Initialize Researcher
        self.coder = CoderAgent(self)  # <--- Initialize Coder
        self.sentinel = SentinelAgent(self)  # <--- Initialize Sentinel
        self.intent_analyzer = IntentAlignment()  # <--- Initialize Intent Analyzer

        logger.info(f"Orchestrator initialized with model: {self.model_name}")

    def intake_sensory_data(self) -> str:
        """
        Reads current system state from observers.
        """
        vitals = self.system_monitor.get_vitality()
        return f"System Vitals: CPU={vitals.cpu_percent}%, RAM={vitals.memory_percent}%"

    def recall_memory(self, query: str) -> str:
        """
        Retrieves relevant context from Vector Memory.
        """
        try:
            results = self.memory.search_memory("knowledge_base", query, n_results=3)
            ids = results.get("ids", [[]])[0]
            documents = results.get("documents", [[]])[0]

            if not ids:
                return ""

            context = "Relevant Knowledge (Vector DB):\n"
            for i, doc in enumerate(documents):
                context += f"- {doc}\n"
            return context
        except Exception as e:
            logger.error(f"Memory recall failed: {e}")
            return ""

    async def process_request(
        self,
        message: str,
        system_prompt: str,
        tools: Optional[List[Any]] = None,
        conversation_history: List[Any] = None,
        fallback_context: str = "",
    ) -> str:
        """
        Processes a user request using the Full CNS Pipeline:
        1. Sensory Intake (System State)
        2. Memory Recall (Vector DB)
        3. Fallback Context (Legacy JSON if needed)
        4. Executive Action (LLM + Tools)
        """
        logger.info(f"Orchestrator processing: {message[:50]}...")
        import time

        start_time = time.time()

        # Directive 376: @CNS Constitution Injection
        if "@CNS" in message:
            logger.info("⚡ CNS SQUAD PROTOCOL ACTIVATED ⚡")
            try:
                # Assuming script runs from root d:/WORK/2/backend/agents/orchestrator.py
                # @CNS.md is at d:/WORK/2/@CNS.md
                manifest_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "../../@CNS.md")
                )
                if os.path.exists(manifest_path):
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        cns_content = f.read()
                    # Prepend to system prompt to give it highest priority
                    system_prompt = f"{cns_content}\n\n{system_prompt}"
                    logger.info("@CNS Constitution injected into System Prompt.")
                else:
                    logger.warning(f"Warning: @CNS.md not found at {manifest_path}")
            except Exception as e:
                logger.warning(f"Failed to load @CNS.md: {e}")

        # 0. Intent Analysis (Directive 374: Brainstorming)
        intent_analysis = self.intent_analyzer.analyze_intent(message)
        if intent_analysis.get("needs_brainstorming"):
            logger.info("Brainstorming Mode Activated.")
            system_prompt += "\n\n" + self.intent_analyzer.get_system_prompt_addition()
            # If in brainstorming mode, we might want to restrict tools or give specific instructions
            # For now, the system prompt addition provides the restriction.

        # 1. Sensory Intake
        sensory_context = self.intake_sensory_data()

        # 2. Memory Recall (Hybrid Strategy)
        memory_context = self.recall_memory(message)

        # Hybrid Logic: If Vector DB returns data, use it.
        # If not, and fallback_context is provided, use that (e.g., full trips list).
        # We can also append fallback_context always if it's critical,
        # but the goal is to reduce context.
        # For safety in this transition phase:
        if not memory_context and fallback_context:
            logger.info("Vector recall empty. Using Fallback Context.")
            final_knowledge_context = f"Fallback Knowledge:\n{fallback_context}"
        else:
            final_knowledge_context = memory_context

        # Prepare History Context
        history_context = ""
        if conversation_history:
            if isinstance(conversation_history, str):
                history_context = f"\n# Chat History\n{conversation_history}"
            elif isinstance(conversation_history, list):
                history_context = "\n# Chat History\n" + "\n".join(
                    [
                        f"{h.get('role', 'user')}: {h.get('text', '')}"
                        for h in conversation_history
                    ]
                )

        augmented_system_prompt = (
            f"{system_prompt}\n\n"
            f"# CNS CONTEXT\n"
            f"{sensory_context}\n"
            f"{final_knowledge_context}\n"
            f"{history_context}"
        )

        # 3. Execution Loop
        try:
            # Prepare contents
            contents = []
            prompt_content = f"{augmented_system_prompt}\n\nUser Message: {message}"

            contents.append(
                types.Content(role="user", parts=[types.Part(text=prompt_content)])
            )

            # Tool-Use Execution Loop (Max 5 turns)
            turn = 0
            while turn < 5:
                response = await self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(tools=tools, temperature=0.4),
                )

                # Check for empty response
                if not response.candidates:
                    return "Error: AI produced no candidates."

                # Check for function calls
                call = next(
                    (
                        p.function_call
                        for p in response.candidates[0].content.parts
                        if p.function_call
                    ),
                    None,
                )

                if not call:
                    # Final text response
                    final_text = response.text.strip()
                    self.memory.add_memory(
                        "knowledge_base",
                        message + " -> " + final_text,
                        {"type": "interaction"},
                    )
                    return final_text

                # Execute tool call
                logger.info(f"Orchestrator requested tool: {call.name}")

                result = "Tool execution failed."
                try:
                    # --- SAFETY GATE ---
                    is_safe = True
                    error_msg = ""

                    # 1. File Modification Safety
                    if (
                        "write_to_file" in call.name
                        or "replace_file_content" in call.name
                    ):
                        target_file = call.args.get("file_path") or call.args.get(
                            "TargetFile"
                        )
                        content = (
                            call.args.get("content")
                            or call.args.get("CodeContent")
                            or call.args.get("ReplacementContent")
                        )

                        if target_file:
                            # A. CREATE SNAPSHOT
                            try:
                                sid = safety_protocol.create_atomic_snapshot(
                                    target_file
                                )
                                logger.info(
                                    f"Safety Snapshot {sid} created for {target_file}"
                                )
                            except Exception as snap_err:
                                logger.warning(
                                    f"Snapshot failed: {snap_err}"
                                )  # Non-blocking for now, but logged

                        if content:
                            # B. STATIC ANALYSIS
                            is_valid, reason = safety_protocol.validate_code_safety(
                                content
                            )
                            if not is_valid:
                                is_safe = False
                                error_msg = f"Safety Protocol Blocked Write: {reason}"

                    # 2. Shell Execution Safety (Redundant with Sandbox but good for depth)
                    elif "execute_shell_command" in call.name:
                        cmd = call.args.get("command")
                        if cmd:
                            is_valid, reason = safety_protocol.validate_code_safety(
                                cmd, "shell"
                            )
                            # Basic check (reusing validate_code_safety which defaults to pass for non-python)
                            # Ideally we add specific shell validation here or rely on SandboxExecutor
                            pass

                    if not is_safe:
                        result = error_msg
                        logger.warning(
                            f"Action blocked by Safety Protocol: {error_msg}"
                        )

                    # --- EXECUTION ---
                    elif call.name == "execute_shell_command":
                        result = "Shell execution not yet fully exposed via MCP."
                    else:
                        result = await mcp_manager.call_tool(call.name, call.args)

                except Exception as tool_err:
                    logger.error(f"Tool execution error: {tool_err}")
                    result = f"Error: {tool_err}"

                # Add exchange to history
                contents.append(response.candidates[0].content)
                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=call.name, result={"output": result}
                                )
                            )
                        ],
                    )
                )
                turn += 1

            return response.text.strip()

        except Exception as e:
            logger.error(f"Orchestrator Error: {e}", exc_info=True)
            return f"System Error: {str(e)}"
        finally:
            if "start_time" not in locals():
                start_time = time.time()
            latency_ms = (time.time() - start_time) * 1000
            if hasattr(self, "sentinel"):
                self.sentinel.analyze_request(latency_ms)
                self.sentinel.check_health()

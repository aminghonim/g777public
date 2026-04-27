import asyncio
import os
import sys
import logging
from typing import List, Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google.genai import types
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    before_log,
    retry_if_exception_type,
)
from backend.core.mcp_auth import MCPAuthenticator

logger = logging.getLogger(__name__)


class MCPManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.sessions: Dict[str, ClientSession] = {}
        self.server_params: Dict[str, StdioServerParameters] = {}
        self.authenticator = MCPAuthenticator()
        self._initialized = True

        # Configure default servers
        self._setup_default_servers()

    def _setup_default_servers(self):
        """Configure the default MCP servers available to the system."""
        # Google Calendar Server (via npx)
        self.server_params["google_calendar"] = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-google-calendar"],
            env=os.environ.copy(),
        )

        # Chrome DevTools Server (WhatsApp Browser)
        self.server_params["chrome-devtools"] = StdioServerParameters(
            command=sys.executable,  # Use current .venv python
            args=[os.path.join(os.getcwd(), "backend/mcp_server/browser.py")],
            env=os.environ.copy(),
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before=before_log(logger, logging.WARNING),
        retry=retry_if_exception_type(Exception),
    )
    async def get_tools_definitions(self, api_key: Optional[str] = None) -> List[types.Tool]:
        """
        Connects to all servers and returns ADK-compliant Tool definitions.
        Requires 'read' or 'full' permission.
        """
        if not self.authenticator.validate(api_key, required_perm="read"):
            logger.warning("Discovery denied: Invalid or missing MCP API key.")
            return []

        all_tools = []
        for server_name, params in self.server_params.items():
            try:
                # Use transient session for discovery
                # In production, we might want to keep sessions alive,
                # but for CLI tools, transient is safer.
                async with stdio_client(params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        mcp_list = await session.list_tools()

                        server_funcs = []
                        for t in mcp_list.tools:
                            # Map MCP Tool -> Gemini FunctionDeclaration
                            func_decl = types.FunctionDeclaration(
                                name=f"{server_name}__{t.name}",
                                description=t.description,
                                parameters=t.inputSchema,
                            )
                            server_funcs.append(func_decl)

                        if server_funcs:
                            # Create one Tool object per MCP Server
                            tool_grp = types.Tool(function_declarations=server_funcs)
                            all_tools.append(tool_grp)

            except Exception as e:
                logger.error(f"Failed to fetch tools from {server_name}: {e}")

        return all_tools

    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any], 
        api_key: Optional[str] = None,
        caller: str = "unknown"
    ) -> str:
        """Route tool calls from the AI back to the correct MCP server."""
        # 🛡️ MCP Auth Layer (M8)
        if not self.authenticator.validate(api_key, required_perm="full"):
            self.authenticator.audit_log(caller, tool_name, success=False)
            return f"Error: Authentication failed for tool {tool_name}. Invalid or missing X-MCP-Token."

        self.authenticator.audit_log(caller, tool_name, success=True)

        if "__" not in tool_name:
            return f"Error: Invalid tool name format {tool_name}"

        server_name, original_name = tool_name.split("__", 1)
        params = self.server_params.get(server_name)
        if not params:
            return f"Error: Server {server_name} not configured."

        try:
            # Use transient session for execution
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(original_name, arguments)

                    # Formatting Result
                    output = []
                    if result.content:
                        for c in result.content:
                            if hasattr(c, "text"):
                                output.append(c.text)
                            elif hasattr(c, "data"):
                                output.append(f"[Binary Data: {len(c.data)} bytes]")

                    return "\n".join(output) if output else "Success (No Output)"

        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            return f"Error executing {tool_name}: {str(e)}"


mcp_manager = MCPManager()

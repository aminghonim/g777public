"""
Module for managing Model Context Protocol (MCP) clients and servers.
Provides a centralized manager for connecting to MCP servers and routing tool calls.
"""
import os
import logging
import json
from typing import List, Dict, Any
from pathlib import Path
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

logger = logging.getLogger(__name__)


class MCPManager:
    """
    Singleton manager for Model Context Protocol (MCP) interactions.
    Handles server configuration, tool discovery, and execution.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.sessions: Dict[str, ClientSession] = {}
        self.server_params: Dict[str, StdioServerParameters] = {}
        self._initialized = True

        # Configure default servers
        self._setup_default_servers()

    def _setup_default_servers(self):
        """Configure the default MCP servers available to the system."""
        # 1. Add Node.js to PATH if possible
        nvm_node_path = "/home/g777/.nvm/versions/node/v24.14.0/bin"
        env = os.environ.copy()
        if os.path.exists(nvm_node_path):
            env["PATH"] = f"{nvm_node_path}:{env.get('PATH', '')}"

        # 2. Hardcoded Google Calendar (as fallback or primary)
        self.server_params["google_calendar"] = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-google-calendar"],
            env=env,
        )

        # 3. Load from mcp_config.json
        config_path = Path(__file__).parent / "mcp_server" / "mcp_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    servers = config.get("mcpServers", {})
                    for name, srv_config in servers.items():
                        # Merge environment
                        srv_env = env.copy()
                        if "env" in srv_config:
                            srv_env.update(srv_config["env"])

                        # Expand environment variables in args
                        raw_args = srv_config.get("args", [])
                        expanded_args = []
                        for arg in raw_args:
                            if isinstance(arg, str):
                                # Expand ${VAR} or $VAR
                                expanded_args.append(os.path.expandvars(arg))
                            else:
                                expanded_args.append(arg)

                        self.server_params[name] = StdioServerParameters(
                            command=srv_config["command"],
                            args=expanded_args,
                            env=srv_env,
                        )
                logger.info("Loaded %d servers from %s", len(servers), config_path)
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Failed to load MCP config from %s: %s", config_path, e)
            except Exception as e:
                logger.error("Unexpected error loading MCP config: %s", e)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before=before_log(logger, logging.WARNING),
        retry=retry_if_exception_type(Exception),
    )
    async def get_tools_definitions(self) -> List[types.Tool]:
        """
        Connects to all servers and returns ADK-compliant Tool definitions.
        Includes Self-Healing Retry Logic.
        """
        all_tools = []
        for server_name, params in self.server_params.items():
            try:
                logger.info("Connecting to MCP server: %s", server_name)
                # Use transient session for discovery
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
                            logger.info("Registered %d tools from %s", len(server_funcs), server_name)

            except Exception as e:
                logger.error("Failed to fetch tools from %s: %s", server_name, e)

        return all_tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Route tool calls from the AI back to the correct MCP server."""
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
            logger.error("Error executing %s: %s", tool_name, e)
            return f"Error executing {tool_name}: {str(e)}"


mcp_manager = MCPManager()

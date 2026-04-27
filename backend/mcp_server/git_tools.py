"""
MCP Git Tools - Token-Optimized via RTK + SmartOutputFilter.

Provides git operations (status, log, commit, sync) as MCP tools
with automatic output compression and audit trail compliance.
All subprocess calls routed through SystemCommandExecutor.
"""

import logging
from mcp.server.fastmcp import FastMCP
from backend.core.system_commands import SystemCommandExecutor

# Initialize MCP Server
mcp = FastMCP("GitKraken")
logger = logging.getLogger("g777.mcp.git_tools")

# Default executor for MCP context (no tenant context in MCP tools)
_DEFAULT_INSTANCE = "mcp_git_tools"


def _get_executor(instance_name: str = _DEFAULT_INSTANCE) -> SystemCommandExecutor:
    """Create a SystemCommandExecutor for the given tenant context."""
    return SystemCommandExecutor(instance_name)


@mcp.tool()
async def get_repo_status() -> str:
    """
    Get current git status with token-optimized output.

    Output is compressed via RTK (if installed) and filtered
    through SmartOutputFilter for signal preservation.
    """
    try:
        executor = _get_executor()
        result = await executor.execute("git status -s")

        if result["status"] == "success":
            output = result.get("output", "").strip()
            return output if output else "Repo is clean."
        return f"Error: {result.get('error', 'Unknown error')}"
    except OSError as exc:
        logger.error(
            "Failed to get repo status",
            extra={"error": str(exc)},
        )
        return f"Error: {exc}"


@mcp.tool()
async def get_recent_commits(count: int = 5) -> str:
    """
    List recent commits with compact output.

    Args:
        count: Number of recent commits to list.
    """
    try:
        executor = _get_executor()
        result = await executor.execute(
            f"git log -n {count} --oneline"
        )

        if result["status"] == "success":
            return result.get("output", "No commits found.")
        return f"Error: {result.get('error', 'Unknown error')}"
    except OSError as exc:
        logger.error(
            "Failed to get recent commits",
            extra={"error": str(exc), "count": count},
        )
        return f"Error: {exc}"


@mcp.tool()
async def commit_changes(message: str) -> str:
    """
    Stage all changes and commit with message.

    Args:
        message: Commit message for the staged changes.
    """
    try:
        executor = _get_executor()

        # Stage all changes
        stage_result = await executor.execute("git add .")
        if stage_result["status"] != "success":
            return f"Staging failed: {stage_result.get('error', '')}"

        # Commit with the provided message (escape quotes in message)
        safe_message = message.replace('"', '\\"')
        commit_result = await executor.execute(
            f'git commit -m "{safe_message}"'
        )

        if commit_result["status"] == "success":
            return commit_result.get("output", "Commit successful.")
        return f"Commit failed: {commit_result.get('error', '')}"
    except OSError as exc:
        logger.error(
            "Failed to commit changes",
            extra={"error": str(exc), "message": message},
        )
        return f"Error: {exc}"


@mcp.tool()
async def sync_repo() -> str:
    """
    Pull latest changes then push current changes.

    Both pull and push outputs are compressed via the
    RTK + SmartOutputFilter pipeline.
    """
    try:
        executor = _get_executor()

        pull_result = await executor.execute("git pull")
        push_result = await executor.execute("git push")

        pull_output = pull_result.get("output", "")
        push_output = push_result.get("output", "")

        return f"Pull:\n{pull_output}\n\nPush:\n{push_output}"
    except OSError as exc:
        logger.error(
            "Failed to sync repo",
            extra={"error": str(exc)},
        )
        return f"Error: {exc}"


if __name__ == "__main__":
    mcp.run()

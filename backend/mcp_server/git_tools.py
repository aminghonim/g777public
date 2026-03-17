import sys
import os
import subprocess
from mcp.server.fastmcp import FastMCP

# Initialize MCP Server
mcp = FastMCP("GitKraken")


@mcp.tool()
async def get_repo_status() -> str:
    """
    Get current git status.
    """
    try:
        result = subprocess.run(
            "git status -s", shell=True, capture_output=True, text=True
        )
        return result.stdout if result.stdout else "Repo is clean."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def get_recent_commits(count: int = 5) -> str:
    """
    List recent commits.
    """
    try:
        cmd = f"git log -n {count} --oneline"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def commit_changes(message: str) -> str:
    """
    Stage all changes and commit with message.
    """
    try:
        subprocess.run("git add .", shell=True, check=True)
        result = subprocess.run(
            f'git commit -m "{message}"', shell=True, capture_output=True, text=True
        )
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def sync_repo() -> str:
    """
    Pull latest changes then push current changes.
    """
    try:
        pull = subprocess.run("git pull", shell=True, capture_output=True, text=True)
        push = subprocess.run("git push", shell=True, capture_output=True, text=True)
        return f"Pull:\n{pull.stdout}{pull.stderr}\n\nPush:\n{push.stdout}{push.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run()

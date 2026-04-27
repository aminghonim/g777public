import sys
import os
import shutil
from mcp.server.fastmcp import FastMCP

# Initialize MCP Server
mcp = FastMCP("filesystem")

# Restricted to project root for safety
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))


@mcp.tool()
async def list_files(path: str = ".") -> str:
    """
    List files in a specific subdirectory of the project.
    """
    target = os.path.abspath(os.path.join(project_root, path))
    if not target.startswith(project_root):
        return "Permission Denied: Path outside project root."

    try:
        files = os.listdir(target)
        return "\n".join(files)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def read_file_content(filepath: str) -> str:
    """
    Read content of a file.
    """
    target = os.path.abspath(os.path.join(project_root, filepath))
    if not target.startswith(project_root):
        return "Permission Denied."

    try:
        with open(target, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def search_in_files(query: str) -> str:
    """
    Search for a string across all project files.
    """
    results = []
    # Simple search
    for root, dirs, files in os.walk(project_root):
        if ".git" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith((".py", ".md", ".json", ".yaml", ".txt")):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        if query in f.read():
                            results.append(os.path.relpath(full_path, project_root))
                except:
                    continue
    return "\n".join(results) if results else "No matches found."


if __name__ == "__main__":
    mcp.run()

"""Agent Router MCP Server - Routes tasks to specialized agents via Pinecone."""
import os
import sys
import logging
import urllib.request
import urllib.error
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Silence all loggers to prevent protocol interference (CNS Rule 8)
logging.getLogger().handlers.clear()
logging.getLogger().setLevel(logging.ERROR)
for logger_name in ("mcp", "httpx", "urllib3", "pinecone"):
    lg = logging.getLogger(logger_name)
    lg.setLevel(logging.ERROR)
    lg.propagate = False

# Redirect stderr for clean MCP protocol
sys.stdout = sys.stderr

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agent-router")

SKILLS_DIR = os.environ.get(
    "SKILLS_DIR",
    os.path.expanduser("~/.gemini/antigravity/skills"),
)
AGENT_MEMORY = "/home/g777/MYCOMPUTER/work/2/.agent/MEMORY.md"
AGENT_INSTINCTS = "/home/g777/MYCOMPUTER/work/2/.agent/INSTINCTS.md"
PINECONE_INDEX = "agent-router"
PINECONE_NAMESPACE = "agents"
CONFIDENCE_HIGH = 0.85
CONFIDENCE_MIN = 0.70


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
    retry=retry_if_exception_type((urllib.error.URLError, urllib.error.HTTPError, TimeoutError))
)
def _search_pinecone(query: str, top_k: int = 5) -> list:
    """Search Pinecone for matching agents using REST API with Retry policy."""
    api_key = os.environ.get("PINECONE_API_KEY", "")
    host = os.environ.get("PINECONE_HOST")

    if not host:
        # Blocker 1: Config-First Directive - Raise error if host is missing
        raise RuntimeError("CRITICAL: PINECONE_HOST not found in environment variables.")

    url = f"{host}/records/namespaces/{PINECONE_NAMESPACE}/search"
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json",
        "X-Pinecone-API-Version": "2025-04",
    }
    body = json.dumps({
        "query": {
            "inputs": {"text": query},
            "top_k": top_k,
        },
        "fields": ["text", "skill_path", "name", "description"],
    })

    req = urllib.request.Request(
        url, data=body.encode("utf-8"), headers=headers, method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("result", {}).get("hits", [])
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        # Blocker 3: Specific Error Handling
        logging.error(f"Pinecone Search Error: {str(e)}")
        raise e  # Allow tenacity to retry


@mcp.tool()
async def find_best_agent(task: str) -> str:
    """
    Find the best specialized agent for a given task.

    Searches across 156 AI agents to find the most relevant specialist.
    Returns the agent name, confidence score, and skill path.

    Args:
        task: Description of the task you need help with.
    """
    try:
        hits = _search_pinecone(task, top_k=1)
    except Exception as e:
        return f"Router Error: Could not reach agent database. {str(e)}"
        
    if not hits:
        return "No matching agents found. Using default mode."

    lines = ["# Agent Routing Results\n"]
    for i, hit in enumerate(hits):
        score = hit.get("_score", 0)
        fields = hit.get("fields", {})
        agent_id = hit.get("_id", "unknown")
        skill_path = fields.get("skill_path", agent_id)
        name = fields.get("name", agent_id)
        desc = fields.get("description", fields.get("text", ""))

        confidence = "HIGH" if score >= CONFIDENCE_HIGH else (
            "MEDIUM" if score >= CONFIDENCE_MIN else "LOW"
        )

        if i == 0:
            lines.append(f"## Best Match: {name}")
            lines.append(f"- **Confidence:** {confidence} ({score:.0%})")
            lines.append(f"- **Description:** {desc}")
            lines.append(
                f"- **SKILL Path:** `{skill_path}/SKILL.md`"
            )
            lines.append("")

            if score < CONFIDENCE_MIN:
                lines.append(
                    "> WARNING: Low confidence. Please confirm this is "
                    "the right agent before proceeding."
                )
                lines.append("")

            lines.append(
                "**Next Step:** Call `get_agent_instructions` with "
                f"`skill_path=\"{skill_path}\"` to load this "
                "agent's full instructions."
            )
            lines.append("")
        else:
            lines.append(f"{i}. {name} ({score:.0%}) - {desc[:80]}")

    return "\n".join(lines)


@mcp.tool()
async def get_agent_instructions(skill_path: str) -> str:
    """
    Load a specialized agent's full instructions.

    Reads the SKILL.md file and adds enforcement headers
    to ensure the agent's methodology is actually followed.

    Args:
        skill_path: The skill_path returned by find_best_agent.
    """
    # 1. Load Instincts and Memory (ECC Pattern)
    instincts = ""
    if os.path.exists(AGENT_INSTINCTS):
        with open(AGENT_INSTINCTS, "r", encoding="utf-8") as f:
            instincts = f.read()

    memory = ""
    if os.path.exists(AGENT_MEMORY):
        with open(AGENT_MEMORY, "r", encoding="utf-8") as f:
            memory = f.read()

    # 2. Load Base Skill
    skill_file = os.path.join(SKILLS_DIR, skill_path, "SKILL.md")
    if not os.path.exists(skill_file):
        return f"Agent skill file not found: {skill_file}"

    with open(skill_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract agent name from YAML frontmatter
    agent_name = skill_path
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if line.startswith("name:"):
                    agent_name = line.split(":", 1)[1].strip().strip("'\"")
            content = parts[2].strip()

    # 3. Load SAAF Governance Protocol (Unified Protocol)
    governance_path = "/home/g777/MYCOMPUTER/work/2/Artifacts/00_Governance/COMPLIANCE_PROTOCOL.md"
    governance_rules = "Follow standard best practices. Ensure Zero-Regression."
    if os.path.exists(governance_path):
        try:
            with open(governance_path, "r", encoding="utf-8") as f:
                governance_rules = f.read()
        except Exception as e:
            logging.error(f"Failed to read governance protocol: {e}")

    enforcement = f"""
================================================================
  ACTIVE AGENT: {agent_name.upper()}
  ENFORCEMENT LEVEL: MANDATORY (ECC: $0 COST OPTIMIZED)
================================================================

PROJECT MEMORY (WHERE WE LEFT OFF):
{memory[:500]}

DYNAMIC INSTINCTS (PROJECT-LEVEL RULES):
{instincts[:500]}

=========================================
🚨 MANDATORY SAAF GOVERNANCE PROTOCOL 🚨
=========================================
You are operating under strict SAAF governance. You MUST apply the following rules to your execution:
{governance_rules}

Failure to comply with the Phase Gates, TDD protocols, or the Zero-Regression rule will result in immediate rejection of your output.

================================================================
"""
    return enforcement + content


@mcp.tool()
async def get_agent_summary(skill_path: str) -> str:
    """
    Lightweight version - for simple tasks.
    Returns only the agent's core principles (200 words).

    Args:
        skill_path: The skill_path returned by find_best_agent.
    """
    skill_file = os.path.join(SKILLS_DIR, skill_path, "SKILL.md")
    if not os.path.exists(skill_file):
        return f"Agent skill file not found: {skill_file}"

    with open(skill_file, "r", encoding="utf-8") as f:
        content = f.read()

    words = content.split()
    return " ".join(words[:200]) + "\n\n[...summary mode: 200 words max...]"


@mcp.tool()
async def verify_agent_enforcement(agent_name: str, response_text: str) -> str:
    """
    Check if the AI adhered to the selected agent's protocol.
    Verifies the presence of the required fingerprint [AGENT-NAME].

    Args:
        agent_name: Name of the active agent (e.g., 'security-engineer').
        response_text: The full response text from the AI to be audited.
    """
    fingerprint = f"[{agent_name.upper()}]"
    if response_text.strip().startswith(fingerprint):
        return (f"✅ ENFORCEMENT PASSED: Response correctly starts with {fingerprint}. "
                "The specialist protocol was followed.")
    else:
        return (f"❌ ENFORCEMENT FAILED: Response did NOT start with {fingerprint}. "
                "The AI deviated from the specialized agent methodology. "
                "RETRY MANDATORY with explicit enforcement call.")


if __name__ == "__main__":
    # Restore stdout for MCP protocol
    sys.stdout = sys.__stdout__
    mcp.run()

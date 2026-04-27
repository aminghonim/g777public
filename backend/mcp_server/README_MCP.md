# Antigravity G777 - MCP Documentation (Linux)

This file explains how to connect the G777 MCP ecosystem to your AI agent (Claude Desktop, Cline, or our custom Qwen Bridge).

## ✅ Local Configuration (Linux)

All tools are configured to run within the project's virtual environment.

**Project Root:** `/home/g777/MYCOMPUTER/work/2`
**Python Path:** `/home/g777/MYCOMPUTER/work/2/.venv/bin/python3`

### Standard Config (e.g., for Claude Desktop)

Update your `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "g777-antigravity": {
      "command": "/home/g777/MYCOMPUTER/work/2/.venv/bin/python3",
      "args": [
        "/home/g777/MYCOMPUTER/work/2/backend/mcp_server/server.py"
      ]
    },
    "agent-router": {
      "command": "/home/g777/MYCOMPUTER/work/2/.venv/bin/python3",
      "args": [
        "/home/g777/MYCOMPUTER/work/2/backend/mcp_server/agent_router.py"
      ],
      "env": {
        "SKILLS_DIR": "/home/g777/MYCOMPUTER/work/2/.agent/skills"
      }
    }
  }
}
```

## 🚀 Running with Local Qwen (Ollama)

If you are using Qwen via CLI, use the specialized bridge agent:

```bash
python3 backend/qwen_agent.py "Your question here"
```

## 🟢 Troubleshooting
1. Ensure the virtual environment is active: `source .venv/bin/activate`.
2. Ensure Ollama is running: `ollama list`.
3. Check logs in `backend/logs/mcp.log` (if enabled).

---
*CNS Squad - Performance Optimized*

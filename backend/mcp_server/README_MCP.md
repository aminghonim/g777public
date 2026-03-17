This file explains how to connect this MCP server to your Claude Desktop App.

## ✅ Configuration (Auto-Applied)

The `setup_mcp.ps1` script and the agent have already:
1. Created an isolated virtual environment at `backend/mcp_server/.venv`.
2. Installed all necessary dependencies.
3. Updated your `claude_desktop_config.json`.

## Manual Reference

If you ever need to manually configure it, use these details:

**Python Path:**
`D:\WORK\2\backend\mcp_server\.venv\Scripts\python.exe`

**Server Script:**
`D:\WORK\2\backend\mcp_server\server.py`

**Config Entry:**
```json
"g777-antigravity": {
  "command": "D:\\WORK\\2\\backend\\mcp_server\\.venv\\Scripts\\python.exe",
  "args": [
    "D:\\WORK\\2\\backend\\mcp_server\\server.py"
  ]
}
```

## 🚀 Next Step
**Restart Claude Desktop** completely for the changes to take effect.
You should see a "Connected 🟢" status or similar indication if you use the `check_system_status` tool.

import requests
import json

url = "http://localhost:5678/mcp-server/http"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjJiNGE5NS0wNTJjLTQyNjYtYmMxYy04MzY4YWJjODhhM2IiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6IjZlYjhmNTdiLTgzOTYtNDcxNy05MjhkLTFlMmM0MTY4ZmU2NSIsImlhdCI6MTc3MTg0OTc2NX0.6RjJNtQdKTEsAFWjGf_R-NTeRqMtnVWqibB2qO3wR6Y"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

payload = {
    "jsonrpc": "2.0",
    "id": "details",
    "method": "tools/call",
    "params": {
        "name": "get_workflow_details",
        "arguments": {"workflowId": "GJ7tet7JKOd3XQlV"},
    },
}

try:
    with requests.post(
        url, headers=headers, json=payload, timeout=20, stream=True
    ) as response:
        with open("workflow_details.json", "w", encoding="utf-8") as f:
            for line in response.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        f.write(decoded[6:])
                        break
    print("Success. Details saved to workflow_details.json")
except Exception as e:
    print(f"Error: {e}")

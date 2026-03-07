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
    "id": "get_id",
    "method": "tools/call",
    "params": {"name": "search_workflows", "arguments": {"limit": 1}},
}

try:
    with requests.post(
        url, headers=headers, json=payload, timeout=15, stream=True
    ) as response:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    content = decoded_line[6:]
                    data = json.loads(content)
                    if "result" in data and "data" in data["result"]:
                        workflow = data["result"]["data"][0]
                        print(f"ID: {workflow['id']}")
                        print(f"Name: {workflow['name']}")
except Exception as e:
    print(f"Error: {e}")

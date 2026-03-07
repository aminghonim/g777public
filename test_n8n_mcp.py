import requests
import json

url = "http://localhost:5678/mcp-server/http"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjJiNGE5NS0wNTJjLTQyNjYtYmMxYy04MzY4YWJjODhhM2IiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6IjZlYjhmNTdiLTgzOTYtNDcxNy05MjhkLTFlMmM0MTY4ZmU2NSIsImlhdCI6MTc3MTg0OTc2NX0.6RjJNtQdKTEsAFWjGf_R-NTeRqMtnVWqibB2qO3wR6Y"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

payload = {"jsonrpc": "2.0", "id": "1", "method": "tools/list", "params": {}}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

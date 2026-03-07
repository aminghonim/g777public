import requests
import json

url = "http://localhost:5678/api/v1/executions"
# Note: The token provided was for MCP. n8n API usually uses an API Key.
# I will try the JWT token just in case, but it likely requires a Header like 'X-N8N-API-KEY'
# or it might not work at all with a JWT.
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNjJiNGE5NS0wNTJjLTQyNjYtYmMxYy04MzY4YWJjODhhM2IiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6IjZlYjhmNTdiLTgzOTYtNDcxNy05MjhkLTFlMmM0MTY4ZmU2NSIsImlhdCI6MTc3MTg0OTc2NX0.6RjJNtQdKTEsAFWjGf_R-NTeRqMtnVWqibB2qO3wR6Y"

headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

try:
    # Try with Bearer first
    response = requests.get(url, headers=headers, params={"limit": 1}, timeout=10)
    if response.status_code == 200:
        print("Executions fetched successfully:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed with Bearer token. Status: {response.status_code}")
        print(f"Response: {response.text}")

    # Try as X-N8N-API-KEY just in case the user confused the two
    headers_alt = {"X-N8N-API-KEY": token, "Accept": "application/json"}
    response_alt = requests.get(
        url, headers=headers_alt, params={"limit": 1}, timeout=10
    )
    if response_alt.status_code == 200:
        print("\nExecutions fetched successfully using X-N8N-API-KEY:")
        print(json.dumps(response_alt.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")

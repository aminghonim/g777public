import requests

url = "http://127.0.0.1:5678/webhook/whatsapp"
print(f"Testing remote N8N: {url}")

try:
    resp = requests.get(url, timeout=5)
    # 404 or 405 or 200 means it's alive (even if method not allowed)
    # Connection error means it's dead.
    print(f"Status: {resp.status_code}") 
    print("Remote N8N is ALIVE.")
except Exception as e:
    print(f"Remote N8N Failed: {e}")

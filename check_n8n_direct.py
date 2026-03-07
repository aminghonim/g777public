
import requests

url = "http://127.0.0.1:5678/webhook/whatsapp"
print(f"📡 Pinging N8N: {url}")

try:
    resp = requests.post(url, json={"test": "ping_from_G777"}, timeout=5)
    print(f"✅ Status: {resp.status_code}")
    print(f"📝 Response: {resp.text}")
except Exception as e:
    print(f"❌ Connection Error: {e}")

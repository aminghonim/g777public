
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

N8N_URL = os.getenv("N8N_WEBHOOK_URL")

if not N8N_URL:
    print("❌ N8N_WEBHOOK_URL is not set in .env")
    exit(1)

print(f"📡 Testing N8N with SIMPLIFIED payload to: {N8N_URL}")

# This mimics exactly what the new webhook_handler.py sends
test_payload = {
    "phone": "201000000000",
    "message": "This is a test message to verify N8N structure fix.",
    "name": "Debug User",
    "type": "conversation",
    "timestamp": 1700000000,
    "raw": {
        "key": {"remoteJid": "201000000000@s.whatsapp.net"},
        "pushName": "Debug User"
    }
}

try:
    resp = requests.post(N8N_URL, json=test_payload, timeout=10)
    print(f"✅ Status: {resp.status_code}")
    print(f"📝 Response: {resp.text}")
    
    if resp.status_code == 200:
        print("\n🎉 SUCCESS! N8N accepted the new payload format.")
    elif resp.status_code == 400:
        print("\n❌ N8N rejected the payload (Bad Request). Check your workflow input structure.")
    else:
        print(f"\n⚠️ Unexpected response: {resp.status_code}")

except Exception as e:
    print(f"❌ Connection Error: {e}")


import requests
import json
import time

URL = "https://g777-brain-748303506355.europe-west1.run.app/webhook/whatsapp"

payload = {
  "event": "messages.upsert",
  "instance": "G777",
  "data": {
    "key": {
      "remoteJid": "201000000000@s.whatsapp.net",
      "fromMe": False,
      "id": "T123456789"
    },
    "pushName": "Test Agent",
    "message": {
      "conversation": "Hello G777! System check initiated."
    },
    "messageType": "conversation"
  },
  "sender": "201000000000@s.whatsapp.net"
}

print(f"📡 Sending test pulse to: {URL}")
try:
    start = time.time()
    resp = requests.post(URL, json=payload, timeout=10)
    end = time.time()
    
    print(f"⏱️ Latency: {end - start:.2f}s")
    print(f"✅ Status: {resp.status_code}")
    print(f"📄 Response: {resp.text}")
    
except Exception as e:
    print(f"❌ Error: {e}")

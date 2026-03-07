import requests
import json

url = "http://127.0.0.1:8080/webhook/whatsapp"

# Simulation Payload (Matches Baileys Format)
payload = {
    "data": {
        "message": {
            "conversation": "مرحبا، انا مهتم بعروض السفر لشرم الشيخ"
        },
        "key": {
            "remoteJid": "201000000000@s.whatsapp.net",
            "fromMe": False
        }
    }
}

try:
    print(f" Sending simulation payload to {url}...")
    response = requests.post(url, json=payload)
    print(f" Status Code: {response.status_code}")
    print(f" Response: {response.text}")
except Exception as e:
    print(f" Connection Failed: {e}")


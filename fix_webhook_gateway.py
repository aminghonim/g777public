import requests
import json
import time

url = "http://127.0.0.1:8080/webhook/set/G777"
headers = {
    "apikey": "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')",
    "Content-Type": "application/json"
}

# Solution from SOLVED_ISSUES.md: Use Host Gateway IP 172.17.0.1
target_webhook_url = "http://172.17.0.1:5678/webhook/474ea20e-da4d-490c-8b46-4ad6233ac90c"

payload = {
    "webhook": {
        "enabled": True,
        "url": target_webhook_url,
        "webhookByEvents": False,
        "events": ["MESSAGES_UPSERT"]
    }
}

try:
    print(f"🚀 Applying Host Gateway Solution...")
    print(f"🔗 Setting Webhook URL to: {target_webhook_url}")
    
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    
    if response.status_code == 201 or response.status_code == 200:
        print(f"✅ Success! Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        print("\n⚠️ IMPORTANT: According to SOLVED_ISSUES.md, you may need to RESTART the Evolution API container if this doesn't work immediately.")
    else:
        print(f"❌ Failed. Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")

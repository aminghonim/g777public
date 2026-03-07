import requests
import json

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE = "G777"
# Use Public IP with No trailing slash
WEBHOOK_URL = "http://127.0.0.1:5678/webhook/whatsapp"

def force_webhook_fix():
    url = f"{EVO_URL}/webhook/set/{INSTANCE}"
    
    # Comprehensive payload
    payload = {
        "webhook": {
            "enabled": True,
            "url": WEBHOOK_URL,
            "webhookByEvents": False,
            "events": [
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "MESSAGES_SET",
                "SEND_MESSAGE"
            ]
        }
    }
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # 1. First, try to Disable
        print("Disabling old webhook...")
        disable_payload = {"webhook": {"enabled": False, "url": WEBHOOK_URL}}
        requests.post(url, json=disable_payload, headers=headers, timeout=10)
        
        # 2. Re-enable with full events
        print(f"Re-enabling with full events for {WEBHOOK_URL}...")
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    force_webhook_fix()

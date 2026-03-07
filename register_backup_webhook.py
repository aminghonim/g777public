import requests
import json

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE = "G777"
# Pure production URL to n8n
WEBHOOK_URL = "http://127.0.0.1:5678/webhook/whatsapp"

def register_webhook():
    url = f"{EVO_URL}/webhook/set/{INSTANCE}"
    
    # Structure based on what we found in the backup scripts
    payload = {
        "webhook": {
            "enabled": True,
            "url": WEBHOOK_URL,
            "webhookByEvents": False,
            "webhookBase64": False,
            "events": ["MESSAGES_UPSERT"]
        }
    }
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Registering Webhook for {INSTANCE}...")
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    register_webhook()

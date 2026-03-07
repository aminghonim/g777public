import requests
import json

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
# The working production path
WEBHOOK_URL = "http://127.0.0.1:5678/webhook/whatsapp"

def set_global_webhook():
    # Setting webhook at the GLOBAL level
    url = f"{EVO_URL}/settings/set"
    
    payload = {
        "webhook_enabled": True,
        "webhook_url": WEBHOOK_URL,
        "webhook_by_events": False,
        "webhook_base64": False,
        "webhook_events": ["MESSAGES_UPSERT"]
    }
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Setting GLOBAL Webhook to: {WEBHOOK_URL}...")
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    set_global_webhook()

import requests
import os
from dotenv import load_dotenv

load_dotenv()

EVO_URL = os.getenv("EVOLUTION_API_URL", "http://127.0.0.1:8080").rstrip('/')
API_KEY = os.getenv("EVOLUTION_API_KEY", "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')")
INSTANCE = os.getenv("EVOLUTION_INSTANCE_NAME", "G777")
TARGET_WEBHOOK = "https://g777-brain-748303506355.europe-west1.run.app/webhook/whatsapp"

def final_verify():
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    print(f"--- 🛡️ Final Webhook Armor Fix ---")
    
    # Force Set
    payload = {
        "webhook": {
            "enabled": True,
            "url": TARGET_WEBHOOK,
            "webhookByEvents": False,
            "events": ["MESSAGES_UPSERT"]
        }
    }
    
    try:
        url = f"{EVO_URL}/webhook/set/{INSTANCE}"
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code in [200, 201]:
            print(f"✅ SUCCESS: Webhook locked to: {TARGET_WEBHOOK}")
        else:
            print(f"❌ FAILED: {r.status_code} - {r.text}")
            
        # Double Check
        print("\nVerifying current settings on server...")
        r_fetch = requests.get(f"{EVO_URL}/instance/fetchInstances", headers=headers)
        instances = r_fetch.json()
        for i in instances:
            if i.get('instanceName') == INSTANCE or i.get('name') == INSTANCE:
                web = i.get('webhook')
                print(f"Current Webhook on Server: {web}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_verify()

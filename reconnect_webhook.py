
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

# Configuration
EVOLUTION_URL = os.getenv("EVOLUTION_API_URL").rstrip('/')
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME")
API_KEY = os.getenv("EVOLUTION_API_KEY")
CLOUD_RUN_URL = "https://g777-brain-748303506355.europe-west1.run.app"
WEBHOOK_ENDPOINT = f"{CLOUD_RUN_URL}/webhook/whatsapp"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def force_reconnect():
    print(f"🔧 Force Reconnecting Webhook for {INSTANCE_NAME}...")
    
    # 1. DELETE Existing Webhook (if any)
    print("1️⃣ Deleting old webhook...")
    try:
        del_url = f"{EVOLUTION_URL}/webhook/find/{INSTANCE_NAME}" # Some versions use delete endpoint, but let's try setting enabled=false first
        # Evolution v2 doesn't always have a clear DELETE, so we overwrite.
    except:
        pass

    # 2. SET New Webhook (Overwrite)
    print(f"2️⃣ Setting NEW Webhook: {WEBHOOK_ENDPOINT}")
    url = f"{EVOLUTION_URL}/webhook/set/{INSTANCE_NAME}"
    payload = {
        "webhook": {
            "enabled": True,
            "url": WEBHOOK_ENDPOINT,
            "webhookByEvents": False,
            "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE", "SEND_MESSAGE"]
        }
    }
    
    resp = requests.post(url, json=payload, headers=headers)
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.text}")

    if resp.status_code in [200, 201]:
        # 3. RESTART Instance (Critical Step)
        print("3️⃣ Restarting Evolution Instance to apply changes...")
        restart_url = f"{EVOLUTION_URL}/instance/restart/{INSTANCE_NAME}"
        try:
            r_resp = requests.post(restart_url, headers=headers)
            print(f"   Restart Status: {r_resp.status_code}")
        except Exception as e:
            print(f"   Restart Warning: {e}")
            
        print("\n✅ Webhook Reconnected! Waiting 10s for instance to come back online...")
        time.sleep(10)
        print("🎉 READY! Test WhatsApp now.")
    else:
        print("\n❌ Failed to set webhook.")

if __name__ == "__main__":
    force_reconnect()

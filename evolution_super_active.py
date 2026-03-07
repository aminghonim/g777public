
import os
import requests
from dotenv import load_dotenv

load_dotenv()

EVOLUTION_URL = os.getenv("EVOLUTION_API_URL").rstrip('/')
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME")
API_KEY = os.getenv("EVOLUTION_API_KEY")
WEBHOOK_URL = "https://g777-brain-748303506355.europe-west1.run.app/webhook/whatsapp"

headers = {"apikey": API_KEY, "Content-Type": "application/json"}

def super_activate():
    print(f"🚀 SUPER ACTIVATING Evolution for {INSTANCE_NAME}...")
    
    # List of all potential events in modern Evolution API
    all_events = [
        "MESSAGES_UPSERT", "MESSAGES_UPDATE", "MESSAGES_DELETE", 
        "SEND_MESSAGE", "CONTACTS_UPSERT", "CONTACTS_UPDATE", 
        "PRESENCE_UPDATE", "CHATS_UPSERT", "CHATS_UPDATE", "CHATS_DELETE",
        "GROUPS_UPSERT", "GROUPS_UPDATE", "GROUP_PARTICIPANTS_UPDATE",
        "CONNECTION_UPDATE", "CALL"
    ]

    # 1. Set Webhook with ALL possible events
    print("1️⃣ Setting Webhook with ALL Events...")
    set_url = f"{EVOLUTION_URL}/webhook/set/{INSTANCE_NAME}"
    payload = {
        "webhook": {
            "enabled": True,
            "url": WEBHOOK_URL,
            "webhookByEvents": False, # Setting to false means it sends everything or follow events list
            "events": all_events
        }
    }
    
    r = requests.post(set_url, json=payload, headers=headers)
    print(f"   Status: {r.status_code} | Resp: {r.text[:100]}")

    # 2. Check Global Webhook (Some versions use this)
    print("\n2️⃣ Checking/Setting Global Webhook...")
    global_url = f"{EVOLUTION_URL}/webhook/instance" # Some versions use this for global
    try:
        r_global = requests.post(global_url, json=payload, headers=headers)
        print(f"   Global Status: {r_global.status_code}")
    except:
        print("   Global endpoint not available in this version.")

    # 3. Query settings to ensure Webhook is actually on
    print("\n3️⃣ Verifying Settings...")
    find_url = f"{EVOLUTION_URL}/webhook/find/{INSTANCE_NAME}"
    r_find = requests.get(find_url, headers=headers)
    if r_find.status_code == 200:
        data = r_find.json()
        print(f"   Webhook Enabled in DB: {data.get('enabled')}")
        print(f"   Target URL: {data.get('url')}")
    
    # 4. Final Restart
    print("\n4️⃣ Final Hard Restart of Instance...")
    requests.post(f"{EVOLUTION_URL}/instance/restart/{INSTANCE_NAME}", headers=headers)
    print("✅ DONE. Evolution is now forced to send every single event to Cloud Run.")

if __name__ == "__main__":
    super_activate()

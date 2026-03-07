
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
EVOLUTION_URL = os.getenv("EVOLUTION_API_URL").rstrip('/')
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME")
API_KEY = os.getenv("EVOLUTION_API_KEY")
N8N_URL = os.getenv("N8N_WEBHOOK_URL")

headers = {
    "apikey": API_KEY
}

def check_all():
    print("🔍 DIAGNOSTIC MODE: Checking Connections...")
    
    # 1. Check Evolution Instance State
    print("\n1️⃣ Checking Evolution Instance State:")
    try:
        url = f"{EVOLUTION_URL}/instance/connectionState/{INSTANCE_NAME}"
        resp = requests.get(url, headers=headers, timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   State: {resp.json().get('instance', {}).get('state')}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")

    # 2. Check Currently Set Webhook
    print("\n2️⃣ Checking Active Webhook in Evolution:")
    try:
        url = f"{EVOLUTION_URL}/webhook/find/{INSTANCE_NAME}"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            wh = resp.json()
            print(f"   Enabled: {wh.get('enabled')}")
            print(f"   URL: {wh.get('url')}")
            print(f"   Events: {wh.get('events')}")
        else:
            print(f"   ❌ Failed to fetch webhook: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 3. Check N8N Reachability
    print(f"\n3️⃣ Checking N8N Reachability ({N8N_URL}):")
    if not N8N_URL:
        print("   ⚠️ N8N_WEBHOOK_URL is not set in .env")
    else:
        try:
            # We use GET here just to check reachability (n8n might expect POST, will likely return 404 or 405 but that means it's reachable)
            resp = requests.get(N8N_URL, timeout=5)
            print(f"   Status: {resp.status_code} (This confirms reachability)")
        except Exception as e:
            print(f"   ❌ UNREACHABLE: {e}")
            print("   👉 Check if your localto.net tunnel is active!")

if __name__ == "__main__":
    check_all()

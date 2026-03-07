
import requests
import json
import os

# Configuration matching .env
EVOLUTION_API_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE_NAME = "G777"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def check_evolution_config():
    print(f"🕵️‍♂️ DIAGNOSING INSTANCE: {INSTANCE_NAME}")
    print(f"🔗 API URL: {EVOLUTION_API_URL}")
    
    # 1. Check Connection State
    try:
        url = f"{EVOLUTION_API_URL}/instance/connectionState/{INSTANCE_NAME}"
        resp = requests.get(url, headers=headers, timeout=5)
        print("\n[1] CONNECTION STATE:")
        print(f"    Status: {resp.status_code}")
        print(f"    Body: {resp.text}")
    except Exception as e:
        print(f"    ❌ Error: {e}")

    # 2. Check Current Webhook
    try:
        url = f"{EVOLUTION_API_URL}/webhook/find/{INSTANCE_NAME}"
        resp = requests.get(url, headers=headers, timeout=5)
        print("\n[2] CURRENT WEBHOOK CONFIG:")
        print(f"    Status: {resp.status_code}")
        try:
            data = resp.json()
            print(f"    URL: {data.get('webhook', {}).get('url')}")
            print(f"    Enabled: {data.get('webhook', {}).get('enabled')}")
            print(f"    Events: {data.get('webhook', {}).get('events')}")
            print(f"    Full Dump: {json.dumps(data, indent=2)}")
        except:
            print(f"    Body: {resp.text}")
    except Exception as e:
        print(f"    ❌ Error: {e}")

if __name__ == "__main__":
    check_evolution_config()

import requests
import json

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE = "G777"

def check_recent_messages():
    # Fetching last 5 messages from the instance
    url = f"{EVO_URL}/chat/findMessages/{INSTANCE}"
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Checking internal logs for {INSTANCE}...")
        # Get chats first to find a JID or just search all
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        with open("evo_messages_debug.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Last messages saved to evo_messages_debug.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_recent_messages()

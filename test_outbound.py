import requests
import json

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE = "G777"
TARGET_PHONE = "201515449773" # This is the owner JID from logs

def test_send():
    url = f"{EVO_URL}/message/sendText/{INSTANCE}"
    payload = {
        "number": f"{TARGET_PHONE}@s.whatsapp.net",
        "text": "G777 System Check - Bot is Alive and Connected! 🚀\nEverything looks correct now."
    }
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Testing outbound for {INSTANCE} to {TARGET_PHONE}...")
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_send()

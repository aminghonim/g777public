import requests
import json

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE = "G777"

def check_webhook():
    url = f"{EVO_URL}/webhook/find/{INSTANCE}"
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🔍 Checking Webhook Config for instance '{INSTANCE}'...")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Current Webhook Data:\n{json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    check_webhook()

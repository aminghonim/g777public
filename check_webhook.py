import requests
import json

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE = "G777"

def check_webhook():
    try:
        response = requests.get(f"{EVO_URL}/webhook/find/{INSTANCE}", headers={"apikey": API_KEY}, timeout=10)
        print(f"Webhook status for {INSTANCE}:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_webhook()

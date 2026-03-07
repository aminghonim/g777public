import requests
import json

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE = "G777"

def restart_instance():
    # Attempting to restart the specific instance via Evolution API
    url = f"{EVO_URL}/instance/restart/{INSTANCE}"
    headers = {
        "apikey": API_KEY
    }
    
    try:
        print(f"Requesting restart for instance {INSTANCE}...")
        resp = requests.post(url, headers=headers, timeout=20)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    restart_instance()

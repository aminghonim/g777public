import requests
import os
from dotenv import load_dotenv

load_dotenv()

EVO_URL = os.getenv("EVOLUTION_API_URL", "http://127.0.0.1:8080").rstrip('/')
API_KEY = os.getenv("EVOLUTION_API_KEY", "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')")
INSTANCE = os.getenv("EVOLUTION_INSTANCE_NAME", "G777")

def diagnose():
    headers = {"apikey": API_KEY}
    print(f"--- Detailed Instance Search ---")
    
    try:
        url = f"{EVO_URL}/instance/fetchInstances"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            instances = resp.json()
            for i in instances:
                name = i.get('instanceName') or i.get('name')
                print(f"Name: {name}")
                if name == INSTANCE:
                    print(f"Found match! Full data: {i}")
                    # Webhook is often inside a nested object in Evolution v2
                    webhook_data = i.get('webhook')
                    if isinstance(webhook_data, dict):
                        print(f"Webhook Settings: {webhook_data}")
                    else:
                        print(f"Webhook raw: {webhook_data}")
        else:
            print(f"Error: {resp.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    diagnose()

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE = "G777"

def get_instance_details():
    try:
        # Check instance info directly if possible
        r = requests.get(f"{EVO_URL}/instance/fetchInstances", headers={"apikey": API_KEY})
        instances = r.json()
        for i in instances:
            if i.get('instanceName') == INSTANCE or i.get('name') == INSTANCE:
                print(f"--- Instance: {i.get('instanceName') or i.get('name')} ---")
                # In some versions it is inside i['webhook']
                print(f"Webhook Data: {json.dumps(i.get('webhook'), indent=2)}")
                # In some versions it is in i['instance']['webhook']
                if 'instance' in i:
                     print(f"Nested Webhook Data: {json.dumps(i['instance'].get('webhook'), indent=2)}")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    get_instance_details()

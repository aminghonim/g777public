import requests
import json

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"

def check_evolution():
    try:
        response = requests.get(f"{EVO_URL}/instance/fetchInstances", headers={"apikey": API_KEY}, timeout=10)
        if response.status_code == 200:
            instances = response.json()
            for inst in instances:
                print(f"Full Instance Data: {json.dumps(inst, indent=2)}")
                print("-" * 20)
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_evolution()

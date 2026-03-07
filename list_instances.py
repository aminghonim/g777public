import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"

def get_all():
    try:
        r = requests.get(f"{EVO_URL}/instance/fetchInstances", headers={"apikey": API_KEY})
        with open("instances_debug.json", "w") as f:
            json.dump(r.json(), f, indent=4)
        print("Instances saved to instances_debug.json")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    get_all()

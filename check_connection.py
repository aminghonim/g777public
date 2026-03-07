import requests
import json
import yaml
import os


def load_config():
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except:
        return {}


def check_instance():
    config = load_config()
    evo_conf = config.get("evolution_api", {})

    # Check local port 3000 first (Baileys Dev Mode)
    local_url = "http://localhost:3000"
    print(f"--- Checking Local Engine ({local_url}) ---")
    try:
        resp = requests.get(f"{local_url}/status", timeout=2)
        print(f"Local status: {resp.status_code}")
        print(resp.text)
    except:
        print("Local engine not running.")

    # Check Cloud/Evolution URL from config
    EVO_URL = evo_conf.get("url", "http://127.0.0.1:8080")
    API_KEY = evo_conf.get("api_key", "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')")
    INSTANCE = evo_conf.get("instance_name", "G777")

    print(f"\n--- Checking Configured API ({EVO_URL}) ---")
    try:
        response = requests.get(
            f"{EVO_URL}/instance/connectionState/{INSTANCE}",
            headers={"apikey": API_KEY},
            timeout=5,
        )
        print(f"Connection state for {INSTANCE}:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error connecting to {EVO_URL}: {e}")


if __name__ == "__main__":
    check_instance()

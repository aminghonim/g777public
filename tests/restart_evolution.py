import requests

EVOLUTION_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE_NAME = "G777"

def restart_instance():
    print(f" Reconnecting Instance: {INSTANCE_NAME}...")
    
    # Try connecting (this often refreshes the session)
    url = f"{EVOLUTION_URL}/instance/connect/{INSTANCE_NAME}"
    headers = {"apikey": API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        print(f" Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f" Instance '{INSTANCE_NAME}' Restarted Successfully!")
            print(" Please wait 10-15 seconds before testing again.")
        else:
            print(f" Failed to restart: {response.text}")
            
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    restart_instance()


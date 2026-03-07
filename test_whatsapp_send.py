import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

EVO_URL = os.getenv("EVOLUTION_PUBLIC_URL", "http://127.0.0.1:8080")
API_KEY = os.getenv("EVOLUTION_API_KEY", "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')")
INSTANCE = os.getenv("EVOLUTION_INSTANCE_NAME", "G777")

def send_test_message(number, text):
    url = f"{EVO_URL}/message/sendText/{INSTANCE}"
    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY
    }
    payload = {
        "number": number,
        "text": text,
        "delay": 1200,
        "linkPreview": True
    }
    
    print(f"Sending message to {number} via {url}...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Using the number from previous logs or a placeholder
    target_number = "201515449773" # User's owner JID number part
    send_test_message(target_number, "G777 System Check: Testing WhatsApp Outbound Connection.")

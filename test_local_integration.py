import requests
import json
import uuid
from datetime import datetime
import time
import os

# Local Backend URL
BACKEND_URL = "http://localhost:8000/webhook/whatsapp"


def get_secure_token():
    try:
        path = r"d:\WORK\2\.antigravity\secure_session.json"
        with open(path, "r") as f:
            data = json.load(f)
            return data.get("token")
    except:
        return None


def simulate_full_flow():
    token = get_secure_token()
    if not token:
        print(
            "Error: Could not find secure token. Retrying with direct session check..."
        )

    print(
        f"[Phase 1] Simulating Inbound WhatsApp Message to LOCAL Backend: {BACKEND_URL}"
    )

    # Payload mimicking Evolution API v2 / Baileys Service
    payload = {
        "event": "messages.upsert",
        "instanceId": "G777",
        "data": {
            "key": {
                "remoteJid": "201000000000@s.whatsapp.net",
                "fromMe": False,
                "id": f"ABC{int(time.time())}",
            },
            "pushName": "Antigravity Tester",
            "message": {
                "conversation": "Hello G777! I am testing the local integration."
            },
            "messageType": "conversation",
            "messageTimestamp": int(datetime.now().timestamp()),
        },
    }

    headers = {"X-G777-Auth-Token": token, "Content-Type": "application/json"}

    try:
        # Step 1: Hit Backend
        print(f"--- Sending to Python Backend with Token: {token} ---")
        response = requests.post(BACKEND_URL, json=payload, headers=headers, timeout=10)
        print(f"Backend HTTP Status: {response.status_code}")

        if response.status_code == 200:
            print("Backend Response:", response.json())
            print("[Phase 2] Success! The Backend received the message.")
            print("Python Backend should now have forwarded this to n8n.")
            print(
                "Check your n8n local instance (http://localhost:5678) for the execution."
            )
        else:
            print(f"Failed. Backend returned: {response.text}")

    except Exception as e:
        print(f"Connection Error: {e}")
        print("Verify that 'python main.py' is running and listening on port 8000.")


if __name__ == "__main__":
    simulate_full_flow()

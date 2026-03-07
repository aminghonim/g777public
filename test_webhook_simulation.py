import requests
import json
import uuid
from datetime import datetime

# Public URL of the Backend
BACKEND_URL = "http://127.0.0.1:8080/webhook/whatsapp"

def simulate_webhook():
    print(f"🚀 Simulating Inbound WhatsApp Message to {BACKEND_URL}...")
    
    # Payload mimicking Evolution API v2
    payload = {
        "event": "messages.upsert",
        "instanceId": "G777",
        "data": {
            "key": {
                "remoteJid": "201000000000@s.whatsapp.net",
                "fromMe": False,
                "id": str(uuid.uuid4()).upper()
            },
            "pushName": "Simulation Spy",
            "message": {
                "conversation": "TEST_HYBRID_FLOW_CONNECTION"
            },
            "messageType": "conversation",
            "messageTimestamp": int(datetime.now().timestamp())
        }
    }
    
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=10)
        print(f"✅ Backend Response: {response.status_code}")
        print(f"📄 Body: {response.text}")
        
        if response.status_code == 200:
            print("\n🎉 Success! The Backend received the message.")
            print("👉 Now check your n8n dashboard. You should see a new execution for the workflow with ID: 474ea20e...")
        else:
            print(f"❌ Failed. Backend returned error.")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("💡 verify that the backend container is running and port 8080 is exposed.")

if __name__ == "__main__":
    simulate_webhook()

import requests
import json

# Testing the PRODUCTION webhook address
N8N_WEBHOOK_URL = "http://127.0.0.1:5678/webhook/whatsapp"

def test_n8n():
    # Simulated Evolution API payload
    payload = {
        "event": "messages.upsert",
        "instance": "G777",
        "data": {
            "key": {
                "remoteJid": "201515449773@s.whatsapp.net",
                "fromMe": False,
                "id": "SIMULATED_ID"
            },
            "pushName": "Test Engineer",
            "message": {
                "conversation": "اختبار النظام - هل n8n يعمل؟"
            },
            "messageType": "conversation"
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending simulated message to n8n at {N8N_WEBHOOK_URL}...")
        resp = requests.post(N8N_WEBHOOK_URL, json=payload, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_n8n()

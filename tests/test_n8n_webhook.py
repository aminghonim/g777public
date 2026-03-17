import requests
import json
import os
from dotenv import load_dotenv

# Load config
load_dotenv(r"d:\WORK\2\.env")

WEBHOOK_URL = "http://127.0.0.1:5678/webhook/whatsapp"  # n8n Webhook URL
TEST_PHONE = "201097752711"  # Real test phone number

def test_workflow():
    print(f" Testing n8n Workflow at: {WEBHOOK_URL}")
    print("=" * 50)

    # 1. Simulate WhatsApp Incoming Message
    payload = {
        "key": {
            "remoteJid": f"{TEST_PHONE}@s.whatsapp.net"
        },
        "pushName": "Test User",
        "message": {
            "conversation": "عايز احجز رحلة لراس سدر 3 ايام"
        }
    }
    
    try:
        print(f"📤 Sending mock message: {payload['message']['conversation']}")
        response = requests.post(WEBHOOK_URL, json=payload)
        
        print(f"📥 Response Code: {response.status_code}")
        print(f" Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n Webhook received the message successfully.")
            print("👉 Now check n8n Executions & Supabase 'customer_memory' table.")
        else:
            print(" Failed to reach n8n webhook only.")
            
    except Exception as e:
        print(f" Connection Error: {e}")
        print("Note: Ensure n8n is running and the workflow is ACTIVATE.")

if __name__ == "__main__":
    test_workflow()


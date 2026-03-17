import requests
import json
import time
import uuid

# Configuration
# Trring to guess the n8n webhook URL based on known IP and standard port
# If this is wrong, please change it manually
N8N_URL = "http://127.0.0.1:5678/webhook/g777-travel-prod" 

def send_message(phone, text, execution_id):
    payload = {
        "event": "messages.upsert",
        "instance": "SENDER",
        "data": {
            "key": {
                "remoteJid": f"{phone}@s.whatsapp.net",
                "fromMe": False,
                "id": str(uuid.uuid4())
            },
            "pushName": "TestBot User",
            "message": {
                "conversation": text
            },
            "messageTimestamp": int(time.time())
        }
    }
    
    print(f"[{execution_id}] 📤 Sending: '{text}' ...")
    try:
        start = time.time()
        response = requests.post(N8N_URL, json=payload, timeout=20)
        duration = round(time.time() - start, 2)
        
        if response.status_code == 200:
            print(f"[{execution_id}]  Success ({dict(response.headers).get('content-length', 0)} bytes) - took {duration}s")
        else:
            print(f"[{execution_id}]  Failed: Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"[{execution_id}]  Connection Failed! (Is n8n running on {N8N_URL}?)")
    except Exception as e:
        print(f"[{execution_id}]  Error: {e}")

if __name__ == "__main__":
    test_phone = "201099988877" # Random test number
    print(f"🚦 Starting Sequence Test for User: {test_phone}")
    print(f"🎯 Target URL: {N8N_URL}\n")

    # 1. First Message (New User)
    send_message(test_phone, "السلام عليكم", 1)
    
    time.sleep(3)
    
    # 2. Second Message (Existing User - This usually fails if upsert logic is wrong)
    send_message(test_phone, "عايز اعرف اسعار راس سدر", 2)
    
    time.sleep(3)
    
    # 3. Third Message
    send_message(test_phone, "طب فيه داي يوز؟", 3)


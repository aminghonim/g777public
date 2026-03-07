import requests
import json
import time

# Target: Local Baileys Service
baileys_url = "http://localhost:3000/webhook/set"
webhook_target = "http://127.0.0.1:8080/webhook/whatsapp"

try:
    print(f" Configuring Baileys Webhook...")
    print(f"   Target: {baileys_url}")
    print(f"   Payload: {webhook_target}")
    
    response = requests.patch(
        baileys_url, 
        json={"url": webhook_target},
        timeout=5
    )
    
    if response.status_code == 200:
        print(f" Success! Webhook linked.")
        print(f" Response: {response.text}")
    else:
        print(f" Warning: Status {response.status_code}")
        print(f" Response: {response.text}")
        
except Exception as e:
    print(f" Failed to configure webhook: {e}")


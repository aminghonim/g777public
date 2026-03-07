import requests
import json

EVO_URL = "http://127.0.0.1:8080"
API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE = "G777"

def check_internal_reachability():
    # Using the /chat/fetchProfile endpoint or similar to trigger an internal outbound request
    # But better, let's just use the Proxy/Query if available. 
    # Actually, Evolution doesn't have a direct 'ping' tool, 
    # so we will check the instance settings to see if the webhook URL is clean.
    
    url = f"{EVO_URL}/webhook/find/{INSTANCE}"
    headers = {"apikey": API_KEY}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        print(f"Current Configured Webhook: {data.get('url')}")
        
        # Now let's try to 'Reset' it one more time to the Docker Gateway IP 
        # which is 172.17.0.1 (common for n8n in your setup)
        GATEWAY_URL = "http://172.17.0.1:5678/webhook/whatsapp"
        print(f"Testing fallback to Gateway IP: {GATEWAY_URL}...")
        
        set_url = f"{EVO_URL}/webhook/set/{INSTANCE}"
        payload = {
            "webhook": {
                "enabled": True,
                "url": GATEWAY_URL,
                "webhookByEvents": False,
                "events": ["MESSAGES_UPSERT"]
            }
        }
        
        set_resp = requests.post(set_url, json=payload, headers=headers, timeout=10)
        print(f"Set Status: {set_resp.status_code}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_internal_reachability()

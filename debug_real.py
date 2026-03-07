import requests
import json
import os

# Real Config from .env
EVO_URL = "http://127.0.0.1:8080"
INSTANCE = "G777"
HEADERS = {"apikey": "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"}

def debug_fetch_participants_real():
    print(f"--- Connecting to Real Server: {EVO_URL} ---")
    
    # 1. Fetch Groups
    try:
        url = f"{EVO_URL}/group/fetchAllGroups/{INSTANCE}?getParticipants=false"
        print(f"GET {url}")
        res = requests.get(url, headers=HEADERS, timeout=10)
        
        print(f"Status: {res.status_code}")
        try:
            data = res.json()
        except:
            print("Response is not JSON:", res.text)
            return

        groups = []
        if isinstance(data, list): groups = data
        elif isinstance(data, dict): 
            groups = data.get('groups') or data.get('instance', {}).get('groups') or []
            
        print(f"Groups Found: {len(groups)}")
        
        if not groups:
            print("FULL RESPONSE:", json.dumps(data, indent=2))
            return

        # 2. Fetch Participants for first group
        target_group = groups[0]
        jid = target_group.get('id')
        subject = target_group.get('subject')
        print(f"\n--- Fetching Participants for: {subject} ({jid}) ---")
        
        url_part = f"{EVO_URL}/group/getParticipants/{INSTANCE}?groupJid={jid}"
        res2 = requests.get(url_part, headers=HEADERS, timeout=15)
        data2 = res2.json()
        
        print("\n[DEBUG] RAW PARTICIPANTS RESPONSE:")
        print(json.dumps(data2, indent=2, ensure_ascii=False)[:2000]) 
        
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

if __name__ == "__main__":
    debug_fetch_participants_real()

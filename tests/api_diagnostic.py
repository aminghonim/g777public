
import requests
import json
import os

URL = "http://127.0.0.1:8080"
KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE = "G777"
HEADERS = {"apikey": KEY, "Content-Type": "application/json"}

def test_api():
    print(f"--- Testing Evolution API for Instance: {INSTANCE} ---")
    
    # 1. Connection State
    print("\n1. Checking Connection State...")
    try:
        res = requests.get(f"{URL}/instance/connectionState/{INSTANCE}", headers=HEADERS)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e: print(f"Error: {e}")

    # 2. Fetch All Groups
    print("\n2. Fetching All Groups...")
    groups = []
    try:
        res = requests.get(f"{URL}/group/fetchAllGroups/{INSTANCE}?getParticipants=false", headers=HEADERS)
        print(f"Status: {res.status_code}")
        data = res.json()
        if isinstance(data, list): groups = data
        elif isinstance(data, dict): 
            # Check common keys
            groups = data.get('groups') or data.get('data') or data.get('instance', {}).get('groups') or []
        
        print(f"Groups Found: {len(groups)}")
        if groups:
            print(f"First Group Sample: {json.dumps(groups[0], indent=2, ensure_ascii=False)}")
    except Exception as e: print(f"Error: {e}")

    # 3. Get Participants (if group found)
    if groups:
        jid = groups[0].get('id')
        print(f"\n3. Fetching Participants for: {jid}...")
        try:
            res = requests.get(f"{URL}/group/getParticipants/{INSTANCE}?groupJid={jid}", headers=HEADERS)
            print(f"Status: {res.status_code}")
            print(f"RAW Response (first 500 chars): {res.text[:500]}")
        except Exception as e: print(f"Error: {e}")

    # 4. Check Numbers Exist
    print("\n4. Checking Numbers Exist (Filter)...")
    try:
        payload = {"numbers": ["201097752711"]}
        res = requests.post(f"{URL}/chat/whatsappNumbers/{INSTANCE}", json=payload, headers=HEADERS)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    test_api()

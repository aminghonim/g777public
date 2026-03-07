import requests
import json
import os
import sys

# Load Config logic simplified
EVO_URL = "http://localhost:8081" # Or whatever port, assuming standard
INSTANCE = "OpenClaw" # Assuming standard
HEADERS = {"apikey": "B6D711FCDE4D4FD5936544120E713976"}

def debug_fetch_participants():
    # 1. First get groups to find a valid JID
    print("--- 1. Fetching Groups ---")
    try:
        res = requests.get(f"{EVO_URL}/group/fetchAllGroups/{INSTANCE}?getParticipants=false", headers=HEADERS)
        data = res.json()
        
        groups = []
        if isinstance(data, list): groups = data
        elif isinstance(data, dict): 
            groups = data.get('groups') or data.get('instance', {}).get('groups') or []
            
        print(f"Groups Found: {len(groups)}")
        if not groups:
            print("FULL RESPONSE:", json.dumps(data, indent=2))
            return

        # Pick the first group
        target_group = groups[0]
        jid = target_group.get('id')
        subject = target_group.get('subject')
        print(f"\n--- 2. Fetching Participants for: {subject} ({jid}) ---")
        
        url = f"{EVO_URL}/group/getParticipants/{INSTANCE}?groupJid={jid}"
        res2 = requests.get(url, headers=HEADERS)
        data2 = res2.json()
        
        print("\n[CRITICAL DEBUG] RAW RESPONSE STRUCTURE:")
        print(json.dumps(data2, indent=2, ensure_ascii=False)[:1000]) # First 1000 chars
        
        # Simulate our logic
        participants = []
        if isinstance(data2, list): participants = data2
        elif isinstance(data2, dict):
            participants = data2.get('participants') or data2.get('data', {}).get('participants') or data2.get('data')
            
        print(f"\nLogic Result: Found {len(participants) if participants else 0} participants.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_fetch_participants()

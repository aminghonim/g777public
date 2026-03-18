
import requests
import json

URL = "http://127.0.0.1:8080"
KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
INSTANCE = "G777"
HEADERS = {"apikey": KEY}
JID = "120363423490128606@g.us" # From previous valid output

def test_group_infos():
    print(f"--- Testing findGroupInfos for {JID} ---")
    url = f"{URL}/group/findGroupInfos/{INSTANCE}?groupJid={JID}"
    try:
        res = requests.get(url, headers=HEADERS)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            # Determine structure
            participants = []
            if isinstance(data, dict):
                 participants = data.get('participants', [])
            
            print(f"Structure Keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            print(f"Participants Found: {len(participants)}")
            if participants:
                print(f"Sample: {participants[0]}")
        else:
            print(f"Error Body: {res.text}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_group_infos()

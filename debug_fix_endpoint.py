import requests
import json

EVO_URL = "http://127.0.0.1:8080"
INSTANCE = "G777"
HEADERS = {"apikey": "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"}

def test_alternate_endpoint():
    print(f"Testing Alternate Endpoint for Participants...")
    # Using a known group JID from previous run
    test_jid = "120363423490128606@g.us" 
    
    # Try different potential endpoints
    endpoints = [
        f"{EVO_URL}/group/participants/{INSTANCE}?groupJid={test_jid}", # v2 style
        f"{EVO_URL}/chat/find/{INSTANCE}/{test_jid}", # Chat info usually contains participants
        f"{EVO_URL}/group/findGroupInfos/{INSTANCE}?groupJid={test_jid}" # Group info
    ]
    
    for url in endpoints:
        print(f"\nTRYING: {url}")
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                print("SUCCESS! Found working endpoint.")
                print(json.dumps(res.json(), indent=2)[:500])
                return
            else:
                print(f"Failed ({res.status_code})")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_alternate_endpoint()

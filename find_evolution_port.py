import requests

PORTS = [8080, 8081, 8082, 8083, 8084, 8085, 3000, 8090]
HOST = "http://127.0.0.1"

print("Scanning for Evolution API...")

found_port = None

for port in PORTS:
    url = f"{HOST}:{port}"
    print(f"Checking {url}...")
    try:
        # Try a known Evolution API endpoint
        test_url = f"{url}/instance/fetchInstances"
        resp = requests.get(test_url, headers={"apikey": "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"}, timeout=2)
        
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            content_type = resp.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                try:
                    data = resp.json()
                    print(f"  FOUND JSON RESPONSE on port {port}!")
                    print(f"  Data: {str(data)[:100]}")
                    print(f"\nEVOLUTION API IS ON PORT {port}")
                    found_port = port
                    break
                except:
                    print("  Not JSON content")
            else:
                 print(f"  Not JSON Type: {content_type}")
        else:
            print(f"  Error Status: {resp.status_code}")
            # Check if 401 Unauthorized (Means service is there but key wrong)
            if resp.status_code == 401:
                print(f"  Auth Failed (Service Exists!) on port {port}")
                found_port = port
                break
            # Check 404 (Endpoint might be different but service active?)
            if resp.status_code == 404:
                 print(f"  404 Not Found (Service active?)")
            
    except Exception as e:
        print(f"  Connection Failed: {e}")

if found_port:
    print(f"Targeting Port {found_port} for Reset...")
    # NOW PERFORM THE RESET LOGIC
    API_URL = f"{HOST}:{found_port}"
    API_KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
    INSTANCE = "G777"
    HEADERS = {"apikey": API_KEY, "Content-Type": "application/json"}
    
    # 1. Force Logout
    print("Executing Force Logout...")
    try:
        requests.delete(f"{API_URL}/instance/logout/{INSTANCE}", headers=HEADERS)
    except: pass
    
    # 2. Wait
    import time
    time.sleep(2)
    
    # 3. Connect (Get QR)
    print("Requesting New Connection...")
    try:
        r = requests.get(f"{API_URL}/instance/connect/{INSTANCE}", headers=HEADERS)
        if r.status_code == 200:
             print("SUCCESS! QR Code Generated.")
             print(r.text[:200])
        else:
             print(f"Failed to get QR: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Could not find Evolution API on any common port.")

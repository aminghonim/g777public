import requests
import json
import time

URL = "http://localhost:8080/webhook/health"
print(f"Checking HEALTH at: {URL}")
try:
    resp = requests.get(URL, timeout=5)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")
    
    if resp.status_code == 200:
        print("\nChecking log file for evidence...")
        time.sleep(2)
        try:
            with open("webhook_incoming.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
                last_lines = lines[-5:]
                found = False
                for line in last_lines:
                    if "TEST_INTERNAL_WEBHOOK_RECEPTION" in line:
                        print(f"FOUND IN LOG: {line.strip()[:100]}...")
                        found = True
                        break
                if not found:
                    print("Request succeeded but NOT found in log (Background task delay?)")
        except Exception as e:
            print(f"Could not read log file: {e}")

except Exception as e:
    print(f"Connection Failed: {e}")
    print("Verify that main.py is running and listening on port 8080.")

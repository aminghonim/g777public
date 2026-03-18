
import requests
import sys
import time

def check_service(name, url, expected_status=200):
    print(f"🔍 Checking {name} at {url}...")
    try:
        start = time.time()
        resp = requests.get(url, timeout=5)
        latency = (time.time() - start) * 1000
        
        if resp.status_code == expected_status:
            print(f" {name} is UP (Status: {resp.status_code}, Latency: {latency:.2f}ms)")
            return True, resp
        else:
            print(f" {name} returned unexpected status: {resp.status_code}")
            print(f"   Response: {resp.text[:200]}")
            return False, resp
    except requests.exceptions.ConnectionError:
        print(f" {name} is DOWN (Connection Refused)")
        return False, None
    except Exception as e:
        print(f" {name} Error: {str(e)}")
        return False, None

def diagnose():
    print("=========================================")
    print("🤖 G777 SYSTEM DIAGNOSTIC TOOL")
    print("=========================================")
    
    # 1. Check Backend Health
    backend_url = "http://localhost:8080"
    backend_up, _ = check_service("Backend API", f"{backend_url}/webhook/health")
    
    # 2. Check Baileys Service (WhatsApp)
    baileys_url = "http://localhost:3000"
    baileys_up, baileys_resp = check_service("Baileys Service", f"{baileys_url}/health")
    
    if baileys_up:
        # Check connection status
        try:
            status = requests.get(f"{baileys_url}/status", timeout=5).json()
            if status.get('connected'):
                print(" WhatsApp Status: CONNECTED")
            else:
                print(" WhatsApp Status: DISCONNECTED (Scan QR Code!)")
                print(f"   QR URL: {baileys_url}/qr")
        except:
            print(" Could not verify WhatsApp internal status")

    print("\n-----------------------------------------")
    if backend_up and baileys_up:
        print("🎉 SYSTEM LOOKS HEALTHY (Locally)")
    else:
        print("🛑 SYSTEM HAS ISSUES")
        print("   If you are testing the Cloud Server, please update the URL in this script.")
    print("=========================================")

if __name__ == "__main__":
    diagnose()


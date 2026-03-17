
import requests
import sys
import time

# Target Server IP (Confirmed)
SERVER_IP = "127.0.0.1"

def check_service(name, url, expected_status=200):
    print(f"🔍 Checking {name} at {url}...")
    try:
        start = time.time()
        # Reduced timeout to 5s to fail fast
        resp = requests.get(url, timeout=5)
        latency = (time.time() - start) * 1000
        
        if resp.status_code == expected_status:
            print(f" {name} is UP (Status: {resp.status_code}, Latency: {latency:.2f}ms)")
            return True, resp
        else:
            print(f" {name} is reachable but returned: {resp.status_code}")
            return False, resp
    except requests.exceptions.ConnectTimeout:
        print(f" {name} Timed Out (Firewall or Service Down)")
        return False, None
    except requests.exceptions.ConnectionError:
        print(f" {name} Connection Refused (Service Not Running)")
        return False, None
    except Exception as e:
        print(f" {name} Error: {str(e)}")
        return False, None

def diagnose():
    print("=========================================")
    print(f"🚑 G777 REMOTE DIAGNOSIS ({SERVER_IP})")
    print("=========================================")
    
    # 1. Check Baileys Service (Port 3000)
    baileys_url = f"http://{SERVER_IP}:3000"
    baileys_up, _ = check_service("WhatsApp Service", f"{baileys_url}/health")
    
    # 2. Check Connection Status (if Service is UP)
    if baileys_up:
        try:
            status = requests.get(f"{baileys_url}/status", timeout=5).json()
            if status.get('connected'):
                print(" WhatsApp Session: CONNECTED ")
            else:
                print(" WhatsApp Session: DISCONNECTED ")
                print("   Action Required: Re-scan QR Code")
        except:
            print(" Could not verify session status")

    print("\n-----------------------------------------")

    # 3. Check Backend (Port 8080)
    backend_url = f"http://{SERVER_IP}:8080"
    backend_up, _ = check_service("Backend Brain", f"{backend_url}/webhook/health")

    print("=========================================")
    
    if not backend_up:
        print(" Diagnosis: The Brain (Backend) seems DOWN.")
        print("   This is why it's not replying.")
        print("   Recommended: SSI into server and restart docker.")

if __name__ == "__main__":
    diagnose()


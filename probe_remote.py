import requests
import socket

TARGET_IP = "127.0.0.1"
PORTS = [8080, 8081, 3000, 5678]

def probe_port(port):
    url = f"http://{TARGET_IP}:{port}"
    print(f"\n--- Probing {url} ---")
    try:
        # distinct verify=False to ignore SSL issues if any, though we use http
        response = requests.get(url, timeout=3)
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Preview: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Probing Server: {TARGET_IP}")
    for p in PORTS:
        probe_port(p)

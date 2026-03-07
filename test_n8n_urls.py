import requests

def test_url(url):
    try:
        print(f"Testing URL: {url}")
        resp = requests.get(url, timeout=5) # Webhook node usually accepts GET too if configured, but let's just check reachability
        print(f"GET Status: {resp.status_code}")
        
        resp = requests.post(url, json={}, timeout=5)
        print(f"POST Status: {resp.status_code}")
        return resp.status_code
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Test path-based
    test_url("http://127.0.0.1:5678/webhook/whatsapp")
    print("-" * 20)
    # Test webhookId-based
    test_url("http://127.0.0.1:5678/webhook/g777-travel-prod")

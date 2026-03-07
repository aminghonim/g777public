
import requests
import json

def test_proxy_with_requests():
    url = "http://127.0.0.1:8045/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-addaf3f6a20741dfb1a71d93f8ec5fac"
    }
    # Trying a safer model name or letting proxy handle default
    data = {
        "model": "gemini-1.5-flash",
        "messages": [{"role": "user", "content": "Say hello!"}]
    }

    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_proxy_with_requests()


import requests
import json

def test_gemini_endpoint():
    # This matches the /v1beta/models endpoint from your question
    url = "http://127.0.0.1:8045/v1beta/models/gemini-pro:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": "sk-addaf3f6a20741dfb1a71d93f8ec5fac" # Your local proxy key
    }
    data = {
        "contents": [{
            "parts":[{"text": "Give me a one-word inspiration."}]
        }]
    }

    print(f"Testing Gemini Protocol via Proxy: {url}")
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Result: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini_endpoint()

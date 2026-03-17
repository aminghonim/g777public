
from google import genai
import os

def test_gemini_stable():
    print("Testing Stable Gemini Connection...")
    
    # Setting the environment variable that the SDK looks for
    os.environ["GOOGLE_GENAI_API_ENDPOINT"] = "http://127.0.0.1:8045"
    
    try:
        # Default initialization uses the environment endpoint
        client = genai.Client(api_key="AIzaSyDBrn8vJ3k1Xu86VhdNHSse9ybbJyxDG2g")
        
        # We use a model that exists in your config
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say 'Proxy connection successful' in one sentence."
        )
        
        print("\n" + "="*50)
        print(f"RESPONSE: {response.text}")
        print("="*50)
        print("\nSUCCESS!")
        
    except Exception as e:
        print(f"FAILED: {e}")
        print("\nChecking if proxy is up...")
        import requests
        try:
            r = requests.get("http://127.0.0.1:8045/healthz")
            print(f"Proxy Health: {r.status_code} - {r.text}")
        except:
            print("Proxy is UNREACHABLE.")

if __name__ == "__main__":
    test_gemini_stable()

"""
Quick Gemini API Key Test (Using google-genai SDK)
"""
import os
from google import genai
from google.genai import types

def clean_key(key):
    if not key: return ""
    return key.strip().replace("'", "").replace('"', "")

def get_key_from_env_raw():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    return line.split('=', 1)[1]
    except:
        return None
    return None

def run_test():
    print("🕵️ GEMINI API KEY TEST")
    print("=" * 40)
    
    # 1. READ KEY
    raw_val = get_key_from_env_raw()
    clean_val = clean_key(raw_val)
    
    if not clean_val:
        print(" ERROR: GEMINI_API_KEY not found in .env")
        return False

    print(f"🔑 Key: {clean_val[:10]}...{clean_val[-10:]} (Length: {len(clean_val)})")
    
    # 2. TEST CONNECTION
    client = genai.Client(api_key=clean_val)
    
    print(" Testing connection to Gemini 2.0 Flash...")
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents='Say exactly: PONG'
        )
        result = response.text.strip()
        print(f" SUCCESS! Response: '{result}'")
        return True
    except Exception as e:
        print(f" FAILED: {e}")
        return False

if __name__ == "__main__":
    success = run_test()
    exit(0 if success else 1)


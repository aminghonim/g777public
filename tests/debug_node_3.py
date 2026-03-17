import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration mimicking n8n Node 3
SUPABASE_URL = "https://zbrpwteyldwpqlcxdpmf.supabase.co"
# Using the NEW key we got earlier
API_KEY = os.getenv("SUPABASE_ANON_KEY") 

print(f"🔑 Using Key ending in: ...{API_KEY[-10:] if API_KEY else 'NONE'}")

# Simulate finding a customer memory
phone_test = "201000000001" 

url = f"{SUPABASE_URL}/rest/v1/customer_memory"
params = {
    "phone": f"eq.{phone_test}",
    "select": "*",
    "order": "created_at.desc",
    "limit": "5"
}

headers = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print(f"\n Sending Request to Supabase: {url}")
try:
    response = requests.get(url, headers=headers, params=params)
    
    print(f"\n Status Code: {response.status_code}")
    if response.status_code == 200:
        print(" SUCCESS! Connection is Working.")
        print("Response Data:", json.dumps(response.json(), indent=2))
        print("\n Diagnosis: Since this script worked, the issue in n8n is likely how it gets the 'phone' number.")
    else:
        print(" FAILED! Supabase rejected the connection.")
        print("Response:", response.text)
        print("\n Diagnosis: The URL or Key in n8n is definitely wrong.")

except Exception as e:
    print(f" Error: {e}")


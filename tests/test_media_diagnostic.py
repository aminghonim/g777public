import requests
import base64
import os
import mimetypes

def test_send_media(instance_url, api_key, instance_name, phone, file_path):
    url = f"{instance_url}/message/sendMedia/{instance_name}"
    headers = {"apikey": api_key, "Content-Type": "application/json"}
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode('utf-8')
    
    mime_type, _ = mimetypes.guess_type(file_path)
    
    payload = {
        "number": f"{phone}@s.whatsapp.net",
        "mediatype": "image",
        "mimetype": mime_type or "image/jpeg",
        "caption": f"Test size: {os.path.getsize(file_path)} bytes",
        "media": b64_data,
        "fileName": os.path.basename(file_path)
    }
    
    try:
        print(f"Sending {file_path} ({os.path.getsize(file_path)} bytes)...")
        res = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Settings from your logs
    URL = "http://127.0.0.1:8080"
    KEY = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
    INSTANCE = "G777" # Assuming from Context
    PHONE = "201097752711" 
    
    # Test with small file
    test_send_media(URL, KEY, INSTANCE, PHONE, "d:/WORK/2/data/1.png")
    
    # Test with large file
    test_send_media(URL, KEY, INSTANCE, PHONE, "d:/WORK/2/data/img_uploaded_file")

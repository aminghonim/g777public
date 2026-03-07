import urllib.request
import urllib.error
import urllib.parse
import json

data = json.dumps({"license_key": "G777-ULTRA-MASTER", "hwid": "1234"}).encode("utf-8")
req = urllib.request.Request(
    "http://127.0.0.1:8001/auth/license/activate",
    data=data,
    headers={"Content-Type": "application/json"},
)
try:
    response = urllib.request.urlopen(req, timeout=5)
    print("SUCCESS", response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTPError", e.code, e.read().decode())
except Exception as e:
    print("Exception", e)

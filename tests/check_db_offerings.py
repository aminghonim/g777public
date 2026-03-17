import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db_service import get_all_offerings, get_connection_pool
from dotenv import load_dotenv

load_dotenv()

print(f"Working Directory: {os.getcwd()}")
print(f"DATABASE_URL exists: {bool(os.getenv('DATABASE_URL'))}")

pool = get_connection_pool()
if pool:
    print(" DB Connected")
    try:
        offerings = get_all_offerings(avail=False)
        print(f"Found {len(offerings)} offerings")
        for o in offerings:
            print(f"- {o['name']} ({o['price']}) Category: {o.get('category')}")
    except Exception as e:
        print(f" Error fetching offerings: {e}")
else:
    print(" DB Connection Failed - Check your .env file and DATABASE_URL")


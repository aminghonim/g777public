import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Let's test again directly with the env variable since we just updated it
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Testing URL: {DATABASE_URL}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connected to Supabase Successfully!")

    # Quick test query
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM tenant_settings;")
    count = cursor.fetchone()[0]
    print(f"Number of tenants: {count}")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")

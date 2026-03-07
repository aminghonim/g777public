import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Switch to port 5432 and remove the .pooler part since we are hitting the DB directly
if "6543" in DATABASE_URL:
    url_5432 = DATABASE_URL.replace("6543", "5432")
    print(f"Trying port 5432: {url_5432}")
    try:
        conn = psycopg2.connect(url_5432)
        print(" Connected successfully on 5432!")
        conn.close()
    except Exception as e:
        print(f" Failed on 5432: {e}")

# Try changing the username format
if "postgres." in DATABASE_URL:
    url_no_tenant = DATABASE_URL.replace("postgres.wfccfllcbnlepudnokpu", "postgres")
    print(f"\nTrying without tenant ID in username: {url_no_tenant}")
    try:
        conn = psycopg2.connect(url_no_tenant)
        print(" Connected successfully without tenant ID!")
        conn.close()
    except Exception as e:
        print(f" Failed without tenant ID: {e}")

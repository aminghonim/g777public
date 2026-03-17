import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

print(f" Testing Connection to: {db_url.split('@')[1] if '@' in db_url else 'Invalid URL'}")

try:
    conn = psycopg2.connect(db_url)
    print(" Successfully connected to Supabase PostgreSQL!")
    conn.close()
except Exception as e:
    print("\n CONNECTION FAILED!")
    print(f"Error Details: {e}")
    
    if "password authentication failed" in str(e):
        print("\n Tip: The password might be incorrect. Please check the character case or special characters.")
    elif "SSL" in str(e):
        print("\n Tip: Try adding ?sslmode=require to the end of the DATABASE_URL in .env")


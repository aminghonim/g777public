import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def migrate():
    url = os.getenv('DATABASE_URL')
    if not url:
        print(" DATABASE_URL missing")
        return

    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        
        print(" Adding 'exclude_from_bot' to 'contacts'...")
        cur.execute("ALTER TABLE contacts ADD COLUMN IF NOT EXISTS exclude_from_bot BOOLEAN DEFAULT true")
        
        print(" Adding 'is_blocked' to 'customer_profiles'...")
        cur.execute("ALTER TABLE customer_profiles ADD COLUMN IF NOT EXISTS is_blocked BOOLEAN DEFAULT false")

        print(" Adding 'bot_paused_until' to 'customer_profiles'...")
        cur.execute("ALTER TABLE customer_profiles ADD COLUMN IF NOT EXISTS bot_paused_until TIMESTAMP")  

        
        conn.commit()
        print(" Migration successful!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f" Migration failed: {e}")

if __name__ == "__main__":
    migrate()


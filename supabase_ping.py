import os
import logging
import psycopg2
from dotenv import load_dotenv

# Load database URL from .env file
load_dotenv()

logger = logging.getLogger("supabase-ping")

def keep_supabase_alive():
    url = os.getenv("DATABASE_URL")
    if not url:
        logger.error("DATABASE_URL not found in .env file")
        return

    try:
        # Establish a quick connection to ping the database
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        logger.info("Supabase Activity Ping Successful!")
        cur.close()
        conn.close()
    except Exception as e:
        logger.error("Supabase Ping Failed: %s", e)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    keep_supabase_alive()

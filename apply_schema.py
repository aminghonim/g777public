"""
Apply Neon Database Schema
===========================
Reads neon_schema.sql and applies it to the database
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def apply_schema():
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print(" DATABASE_URL not found in .env")
        return False
    
    print(" Applying Schema to Neon Database...")
    print(f"📍 Database: {database_url.split('@')[1].split('/')[0]}")
    
    # Read SQL file
    schema_path = os.path.join('database', 'schema.sql')
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
    except FileNotFoundError:
        print(f" Schema file not found: {schema_path}")
        return False
    
    # Connect and execute
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Execute schema
        cursor.execute(schema_sql)
        conn.commit()
        
        print(" Schema applied successfully!")
        
        # Verify tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Created Tables:")
        for table in tables:
            print(f"    {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f" Error: {e}")
        return False

if __name__ == "__main__":
    success = apply_schema()
    exit(0 if success else 1)


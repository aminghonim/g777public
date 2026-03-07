#!/usr/bin/env python3
"""
List all tables in Supabase database
"""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.db_service import get_db_cursor

load_dotenv()

def list_tables():
    print("🔍 Listing all tables in Supabase database...")
    print("=" * 60)
    
    with get_db_cursor() as cur:
        if not cur:
            print("❌ Failed to connect to database. Check DATABASE_URL in .env")
            return

        # List all tables
        cur.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        
        if not tables:
            print("📭 No tables found in public schema")
            return
            
        print(f"📊 Found {len(tables)} tables in public schema:")
        print("-" * 40)
        
        for table in tables:
            table_name = table['table_name']
            table_type = table['table_type']
            
            # Get row count for each table
            cur.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            row_count = cur.fetchone()['count']
            
            print(f"📋 {table_name} ({table_type}) - {row_count} rows")
            
            # Get column info for main tables
            if table_name in ['tenant_settings', 'business_offerings', 'customer_profiles', 'conversations', 'messages']:
                cur.execute("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position
                """, (table_name,))
                columns = cur.fetchall()
                print("   Columns:")
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    print(f"     - {col['column_name']}: {col['data_type']} ({nullable})")
                print()
        
        print("=" * 60)
        print("✅ Table listing complete!")

if __name__ == "__main__":
    list_tables()

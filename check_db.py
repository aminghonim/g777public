"""
G777 Modern DB Check - Verify TripiGo / Yasmine Data
"""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.db_service import get_db_cursor, format_offerings_for_prompt

load_dotenv()

def check_db():
    print("🔍 Probing Modern G777 Database...")
    print("=" * 60)
    
    with get_db_cursor() as cur:
        if not cur:
            print(" Failed to connect to database. Check DATABASE_URL in .env")
            return

        # 1. Check Tenant Settings
        cur.execute("SELECT business_name, business_type, identity_prompt FROM tenant_settings ORDER BY created_at DESC LIMIT 1")
        settings = cur.fetchone()
        if settings:
            print(f"🏢 Business: {settings['business_name']} ({settings['business_type']})")
            print(f"🆔 Identity: {settings['identity_prompt'][:100]}...")
        else:
            print(" No tenant settings found!")

        # 2. Check Offerings (Trips)
        cur.execute("SELECT COUNT(*) as count FROM business_offerings")
        off_count = cur.fetchone()['count']
        print(f"\n📦 Offerings (Trips) in DB: {off_count}")
        
        if off_count > 0:
            print("\n📋 Sample Offerings:")
            cur.execute("SELECT name, price, category FROM business_offerings LIMIT 5")
            for row in cur.fetchall():
                print(f"   - {row['name']} | {row['price']} EGP | {row['category']}")
            
            print("\n🤖 Offerings Text for AI:")
            print("-" * 30)
            print(format_offerings_for_prompt()[:300] + "...")
        
        # 3. Check Customers
        cur.execute("SELECT COUNT(*) as count FROM customer_profiles")
        cust_count = cur.fetchone()['count']
        print(f"\n👥 Total Customers: {cust_count}")
        
    print("\n" + "=" * 60)
    print(" Database check complete!")

if __name__ == "__main__":
    check_db()


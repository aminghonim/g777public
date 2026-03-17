"""
Clean Database - Remove sample clothing data
=============================================
This script removes the sample clothing products from the database
to make it clean for any business type.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db_service import get_db_cursor, settings_cache
from dotenv import load_dotenv

load_dotenv()

def clean_sample_data():
    """Remove sample clothing products from database"""
    print("🧹 Cleaning sample data from database...")
    
    with get_db_cursor() as cur:
        if not cur:
            print(" Database connection failed!")
            return False
        
        # Delete clothing sample products
        cur.execute("""
            DELETE FROM business_offerings 
            WHERE name IN ('تيشيرت قطن', 'بنطلون جينز')
            OR category = 'ملابس رجالي'
        """)
        deleted = cur.rowcount
        print(f" Deleted {deleted} sample product(s)")
        
        # Clear cache
        settings_cache.invalidate()
        
    return True

def verify_clean():
    """Verify database is clean"""
    from backend.db_service import get_all_offerings
    offerings = get_all_offerings(avail=False)
    print(f"\n Current offerings in database: {len(offerings)}")
    for o in offerings:
        print(f"   - {o['name']} ({o['price']})")
    
    if len(offerings) == 0:
        print("\n✨ Database is clean! Ready for your business.")

if __name__ == "__main__":
    clean_sample_data()
    verify_clean()


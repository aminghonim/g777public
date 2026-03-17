"""
End-to-End CRM Test
===================
1. Simulates a conversation with a new customer.
2. Triggers the AI Extraction engine.
3. Verifies the data appears in Supabase CRM.
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from backend.db_service import create_customer, create_conversation, save_message, get_customer_by_phone
from backend.crm_intelligence import run_data_extraction

async def test_crm_flow():
    print("🎬 Starting End-to-End CRM Test...")
    print("-" * 50)
    
    # 1. Create Mock Customer
    phone = "201000000001"
    print(f" Creating mock customer: {phone}")
    cust_id = create_customer(phone, name="Test User", ctype="lead")
    
    if not cust_id:
        print(" Failed to create customer.")
        return

    # 2. Create Conversation
    print("💬 Simulating chat history...")
    conv_id = create_conversation(cust_id)
    
    # User message
    save_message(conv_id, cust_id, "user", "السلام عليكم، أنا محمود من الإسكندرية. كنت عايز أسأل على رحلات الداي يوز في راس سدر.")
    # Bot response
    save_message(conv_id, None, "assistant", "وعليكم السلام ورحمة الله وبركاته يا أستاذ محمود، نورتنا. الداي يوز عندنا بـ 450 جنيه شامل الانتقالات والغداء.")
    # User message
    save_message(conv_id, cust_id, "user", "تمام ممتاز. وأنا مهتم جداً بالكايت سيرف كمان. هل السعر شامل ده؟")
    
    # 3. Trigger Intelligence
    print("🧠 Triggering AI Extraction Engine...")
    await run_data_extraction(phone, conv_id)
    
    # 4. Verify Result
    print("-" * 50)
    print("🔍 Verifying CRM Data in Supabase...")
    customer = get_customer_by_phone(phone)
    
    if customer:
        name = customer.get('name')
        city = customer.get('city')
        meta = customer.get('metadata', {})
        interests = meta.get('interests', [])
        
        print(f" Name: {name}")
        print(f" City: {city}")
        print(f" Interests: {interests}")
        
        if city == "الإسكندرية" and any("كيت" in i or "Kite" in i for i in interests):
            print("\n🎉 SUCCESS! The System successfully extracted the data from chat!")
        else:
            print("\n Data Match Warning: Check the output above.")
    else:
        print(" Customer not found in DB.")

if __name__ == "__main__":
    asyncio.run(test_crm_flow())


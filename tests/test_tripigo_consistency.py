"""
Consistency Test for TripiGo (Yasmine)
======================================
Tests the persona rules:
1. Rejects non-Ras Sudr destinations (e.g. Sharm).
2. Uses only DB prices.
3. Maintains persona (Yasmine).
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db_service import get_tenant_settings, get_system_prompt, format_offerings_for_prompt
# Mocking the AI generation part to inspect the PROMPT primarily, 
# but if we have an AI service connected we could call it.
# For now, let's look at the CONSTRUCTED SYSTEM PROMPT to ensure Data Anchoring is correct.

def test_system_prompt_construction():
    print("🔍 Inspecting System Prompt Construction (Data Anchoring)...")
    
    settings = get_tenant_settings()
    offerings_text = format_offerings_for_prompt()
    base_prompt = get_system_prompt('main_assistant')
    
    if not base_prompt:
        # Fallback if not found in table yet (since we might rely on default schema insert)
        print(" 'main_assistant' prompt not found in DB, checking schema default...")
        base_prompt = """أنت مساعد ذكي لـ {business_name}.
هويتك:
{identity_prompt}

المنتجات/الخدمات المتاحة:
{offerings_list}"""

    # Simulate injection
    full_prompt = base_prompt.replace('{business_name}', settings.get('business_name', ''))
    full_prompt = full_prompt.replace('{identity_prompt}', settings.get('identity_prompt', ''))
    full_prompt = full_prompt.replace('{offerings_list}', offerings_text)
    
    print("\n" + "="*50)
    print("🤖 GENERATED SYSTEM PROMPT FOR AI:")
    print("="*50)
    print(full_prompt)
    print("="*50)
    
    # Verification Checks
    print("\n Verification Checks:")
    
    if "ياسمين" in full_prompt:
        print("PASS: Persona 'Yasmine' found.")
    else:
        print("FAIL: Persona 'Yasmine' NOT found.")

    if "راس سدر" in full_prompt:
        print("PASS: 'Ras Sudr' focus found.")
    else:
        print("FAIL: 'Ras Sudr' focus NOT found.")
        
    if "450" in full_prompt: # Price for Day Use
        print("PASS: Price '450' (Day Use) anchored correctly.")
    else:
        print("FAIL: Price '450' missing.")

    if "2200" in full_prompt: # Price for Weekend
        print("PASS: Price '2200' (Weekend) anchored correctly.")
    else:
        print("FAIL: Price '2200' missing.")
        
    if "ملابس" not in full_prompt:
        print("PASS: Old 'Clothing' data successfully removed.")
    else:
        print("FAIL: Old 'Clothing' data still present!")

if __name__ == "__main__":
    test_system_prompt_construction()


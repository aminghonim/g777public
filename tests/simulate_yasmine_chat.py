"""
Simulation: Chat with Yasmine (TripiGo)
=======================================
Simulates a full conversation flow with the AI Agent to test persona and data integrity.
"""

import sys
import os
import requests
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.db_service import get_tenant_settings, get_all_offerings, format_offerings_for_prompt

load_dotenv()

# Simulate the AI Logic locally (since we might not have the full cloud AI connected here)
# This is a RULE-BASED Simulator that mimics exactly how the prompt instructs the AI
def simulate_ai_response(user_message, system_prompt):
    user_msg_lower = user_message.lower()
    
    # 1. Check for Competitor/Wrong Destination
    if any(x in user_msg_lower for x in ['شرم', 'غردقة', 'دهب', 'sharm', 'hurghada']):
        return "أهلاً بحضرتك 💙.. الحقيقة إحنا في TripiGo متخصصين وملوك الروقان في (راس سدر) بس، وعاملين هناك أحلى برامج للكايت سيرف والويك إند. تحب تشوف عروضنا لراس سدر؟ "

    # 2. Check for Price/Offers
    if any(x in user_msg_lower for x in ['بكام', 'سعر', 'price', 'cost']):
        # Scan offerings
        response = "أهلاً يا فندم! دي أحدث عروضنا في TripiGo لراس سدر: \n\n"
        offerings = get_all_offerings()
        for o in offerings:
            name = o.get('name')
            price = o.get('price')
            
            # Match specific requests
            if 'داي' in user_msg_lower and 'day' not in name.lower() and 'يوم' not in name: continue
            if 'مبيت' in user_msg_lower and '3' not in name: continue
            if 'مركب' in user_msg_lower and 'boat' not in name.lower(): continue
            
            response += f" *{name}*: {price} جنيه\n"
            
        return response + "\nتحب أحجزلك حاجة منهم؟"
    
    # 3. Check for Road/Safety
    if 'طريق' in user_msg_lower or 'أمان' in user_msg_lower:
        return "متخافش من الطريق خالص!  الطريق بياخد حوالي 3 ساعات من القاهرة، ومن بعد نفق الشهيد أحمد حمدي الطريق بقى مزدوج وحر وممتاز جداً وأمان."
        
    # Default Greeting
    return "أهلاً بيك في TripiGo! 💙 معك ياسمين.. إزاي أقدر أساعدك تختار رحلتك الجاية لراس سدر؟ 🏄‍♂️"

def run_simulation():
    print("🔵 بدء محادثة تجريبية مع ياسمين (TripiGo)...")
    print("="*60)
    
    # Load Context
    settings = get_tenant_settings()
    offerings_text = format_offerings_for_prompt()
    
    # Scenario 1: Greeting
    print("\n العميل: السلام عليكم")
    print(f"‍ ياسمين: {simulate_ai_response('السلام عليكم', '')}")
    
    # Scenario 2: The Trap (Sharm El Sheikh)
    print("\n العميل: لو سمحتي عندكم رحلات لشرم الشيخ؟")
    print(f"‍ ياسمين: {simulate_ai_response('عندكم رحلات لشرم الشيخ؟', '')}")
    
    # Scenario 3: Price Inquiry (Day Use)
    print("\n العميل: طيب بكام الداي يوز؟")
    print(f"‍ ياسمين: {simulate_ai_response('طيب بكام الداي يوز؟', '')}")
    
    # Scenario 4: Road Question
    print("\n العميل: بس أنا قلقان من الطريق، هل هو أمان؟")
    print(f"‍ ياسمين: {simulate_ai_response('بس أنا قلقان من الطريق، هل هو أمان؟', '')}")
    
    print("\n" + "="*60)
    print(" انتهاء المحاكاة.")

if __name__ == "__main__":
    run_simulation()



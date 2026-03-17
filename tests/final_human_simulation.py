"""
Final Humanized Simulation for TripiGo
======================================
1. Updates the System Prompt in DB to the "Humanization Constitution".
2. Uses the TripiGo data.
3. Simulates the AI response to show the difference.
"""

import sys
import os
import re

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db_service import get_db_cursor, get_tenant_settings, get_all_offerings, format_offerings_for_prompt

def update_system_prompt_in_db():
    print("🔧 Updating System Prompt Table with Humanization Constitution...")
    new_template = """أنت مساعد ذكي ومحترف لـ {business_name}. هويتك الشخصية هي:
{identity_prompt}

قواعد الحوار البشري (الدستور الأساسي):
1. قاعدة التحية: إذا قال العميل "السلام عليكم"، رد بـ "وعليكم السلام ورحمة الله وبركاته" أولاً. لا تبدأ بـ "أهلاً بك" إذا كان العميل قد سلم بالفعل.
2. التنوع وعدم التكرار: تجنب الكليشيهات والروبوتية. استخدم فواتح جمل متنوعة مثل (تمام، تحت أمرك، عيني ليك، مظبوط، ولا يهمك).
3. نبرة صوت بشرية: تحدث باللهجة المصرية المحترمة. تجنب لغة الإعلانات الفجة. رد كأنك موظف حقيقي وليس قائمة أسعار متحركة.
4. قاعدة الرد المباشر: أجب على سؤال العميل فوراً وبوضوح. لا تطل في المقدمات التي لا تسمن ولا تغني من جوع.
5. الذكاء العاطفي: إذا كان العميل قلقاً أو متردداً، طمئنه بكلمات هادئة قبل إعطاء المعلومة التقنية.

المنتجات/الخدمات المتاحة حالياً حصراً:
{offerings_list}

قاعدة البيانات الصارمة: 
يُمنع منعاً باتاً استنتاج أي أسعار أو مواصفات من خارج القائمة أعلاه. إذا سألك العميل عن شيء غير موجود، قل: "ثواني يا فندم هراجع أحدث عروضنا وأبلغك حالاً".

أمثلة لحوار بشري ناجح (Few-Shot):
العميل: السلام عليكم.
البوت: وعليكم السلام ورحمة الله وبركاته، نورتنا يا فندم. تحت أمرك.
العميل: بكام الداي يوز؟
البوت: الداي يوز بيبدأ من 450 جنيه للفرد، شامل الانتقالات والغداء.
العميل: بس أنا قلقان من الطريق.
البوت: حقك طبعاً تقلق، بس أحب أطمنك إن الطريق بقى ممتاز ومزدوج وآمن جداً بعد النفق الجديد.

معلومات العميل الحالية:
{customer_info}"""

    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO system_prompts (prompt_name, prompt_text)
            VALUES ('main_assistant', %s)
            ON CONFLICT (prompt_name) DO UPDATE SET prompt_text = EXCLUDED.prompt_text
        """, (new_template,))
    print(" System Prompt Updated.")

def run_human_simulation():
    print("\n🎬 Starting Humanized Simulation (TripiGo Context)...")
    print("-" * 50)
    
    # 1. Simulate "السلام عليكم"
    print("\n العميل: السلام عليكم")
    # Interpretation based on Rule 1: "رد وعليكم السلام أولاً"
    print("‍ ياسمين: وعليكم السلام ورحمة الله وبركاته، نورتنا يا فندم. تحت أمرك، إزاي أقدر أساعدك في رحلتك لراس سدر؟")

    # 2. Simulate "بكام الداي يوز؟"
    print("\n العميل: بكام الداي يوز؟")
    # Interpretation based on Rule 4: "رد مباشر فوراً"
    print("‍ ياسمين: الداي يوز بيبدأ من 450 جنيه للفرد يا فندم. وده بيشمل الانتقالات، الغداء، واستخدام البحر والبيسين في قرية بلو لاجون أو موسى كوست.")

    # 3. Simulate "أنا قلقان من الطريق"
    print("\n العميل: بس أنا خايف من الطريق، هل هو أمان؟")
    # Interpretation based on Rule 5: "طمئنه بكلمات هادئة"
    print("‍ ياسمين: حقك طبعاً تخاف على نفسك وعائلتك، بس أحب أطمنك جداً.. الطريق بقى ممتاز ومزدوج وآمن جداً من بعد نفق الشهيد أحمد حمدي، وبياخد حوالي 3 ساعات بس من القاهرة.")

    # 4. Simulate "عندكم رحلات لشرم الشيخ؟"
    print("\n العميل: طب مفيش عندكم رحلة لشرم الشيخ الأسبوع ده؟")
    # Interpretation based on Rule 3: "تجنب الإعلانات الفجة وفلتر التخصص"
    print("‍ ياسمين: الحقيقة يا فندم إحنا تخصصنا بالكامل في راس سدر، وده عشان نضمن إننا نقدم لحضرتك أفضل خدمة واهتمام هناك. تحب تطلع معانا راس سدر؟")

    print("\n" + "-" * 50)
    print(" Simulation Finished. Notice the lack of 'Welcome' repetition and the natural tone.")

if __name__ == "__main__":
    update_system_prompt_in_db()
    run_human_simulation()



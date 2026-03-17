"""
Script to generate offline Data for Warmer.
"""
import sys
import os
import json
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pylint: disable=wrong-import-position
from backend.ai_client import UnifiedAIClient

async def generate_offline_warmer_data(count: int = 50):
    """
    Generate phrases via the Intelligent AI Client.
    """
    print(f"Generating {count} Egyptian Arabic casual phrases for Warmer...")
    ai = UnifiedAIClient()
    prompt = (
        f"قم بتوليد {count} رسالة قصيرة (3-7 كلمات) تصلح لبدء محادثة أو الرد العشوائي بين أصدقاء مصريين على واتساب.\n"  # pylint: disable=line-too-long
        "الرسائل يجب أن تكون عامية مصرية طبيعية جداً، ولا تبدو كأنها من بوت.\n"
        "لا تستخدم إيموجي إلا نادراً. لا تستخدم أرقام. \n"
        "أمثلة: 'إيه الأخبار يا صاحبي؟', 'فينك يابني مختفي ليه', 'عامل إيه النهاردة؟', 'تمام يا باشا'.\n"  # pylint: disable=line-too-long
        "أرجع النتائج فقط كمصفوفة JSON (Array of strings) بصيغة صحيحة. لا تضف أي نص آخر."
    )

    system = "أنت شاب مصري يتحدث بلهجة عامية طبيعية على واتساب."

    try:
        response = await ai.generate_response(prompt, system)
        # Clean response to extract JSON
        json_str = response.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]

        phrases = json.loads(json_str.strip())

        if isinstance(phrases, list) and len(phrases) > 0:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")  # pylint: disable=line-too-long
            os.makedirs(config_dir, exist_ok=True)
            output_path = os.path.join(config_dir, "warmer_ar.json")

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(phrases, f, ensure_ascii=False, indent=4)

            print(f"[OK] Successfully saved {len(phrases)} phrases to {output_path}")
        else:
            print("[ERROR] AI did not return a valid list.")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"[ERROR] Failed to generate data: {e}")

if __name__ == "__main__":
    asyncio.run(generate_offline_warmer_data())

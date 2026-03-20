\"\"\"
Antigravity Brain Trainer - Humanization Loop
=============================================
هذا الكود يقوم بـ \"تربية\" ذكاء البوت عن طريق:
1. إرسال أسئلة للبوت (الرد الآلي).
2. تحويل الرد لرد \"بشري\" احترافي باستخدام Gemini Humanizer.
3. حفظ النماذج (Few-Shot) في قاعدة البيانات لاستخدامها كأمثلة تعليمية.
\"\"\"

import asyncio
import os
import json
import requests
from dotenv import load_dotenv
from .ai_client import UnifiedAIClient
from .ai_engine import ai_engine
from .db_service import get_db_cursor
import logging

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

# أسئلة مقترحة للتدريب البنّاء
TRAINING_QUESTIONS = [
    \"بكم سعر رحلة اليوم الواحد لراس سدر؟\",
    \"هل الطريق آمن للسفر بالليل؟\",
    \"ماذا تشمل رحلة الـ 3 أيام؟\",
    \"هل يوجد يخت خاص للمجموعات؟\",
    \"أريد حجز رحلة لشخصين يوم الجمعة القادم\",
    \"ما هو أفضل وقت لزيارة راس سدر؟\",
    \"هل الرحلة شاملة الوجبات؟\",
    \"كيف يمكنني الدفع؟\"
]

class BrainTrainer:
    def __init__(self):
        self.ai = UnifiedAIClient()
        # رابط الـ Webhook بتاع n8n أو الـ Backend المحلي
        self.bot_url = os.getenv(\"BOT_WEBHOOK_URL\", \"http://localhost:5678/webhook/1/whatsapp/g777-travel-prod\")
        
    async def humanize_bot_response(self, question, robotic_response):
        \"\"\"
        تحويل الرد الآلي لرد بشري بلهجة مصرية ودودة جداً
        \"\"\"
        system_prompt = f\"\"\"
        أنت خبير \"أنسنة\" (Humanizer) للذكاء الاصطناعي.
        المهمة: تحويل الرد \"الآلي\" الجامد إلى رد \"بشري\" مصري ودود جداً واحترافي.
        
        تعليمات صارمة:
        1. اكتب الرد النهائي مباشرة بدون أي مقدمات.
        2. اللهجة: مصرية محترمة جداً (رسمية بس عامية). ممنوع \"يا حبيبي\" و\"يا عمري\" نهائياً.
        3. ممنوع التكرار الممل (زي \"ألف أهلاً\" كل مرة).
        4. لو السؤال عن \"أنتِ AI؟\" أو \"روبوت؟\"، الرد: \"لا يا فندم، أنا ياسمين معاك من خدمة العملاء\".
        5. الردود تكون محددة وفي الصميم، بلاش رغي كتير.

        مثال 1 (سعر):
        - السؤال: \"بكام الرحلة؟\"
        - الرد: \"يا فندم السعر 450 جنيه للفرد، شامل الانتقالات والغداء.\"

        مثال 2 (شك):
        - السؤال: \"أنتِ كمبيوتر؟\"
        - الرد: \"لا والله يا فندم، أنا ياسمين موظفة الحجوزات، تحت أمرك.\"
        
        السؤال الأصلي: {question}
        الرد الآلي المطلوب تحسينه: {robotic_response}
        
        الرد البشري المقترح (محترم ومحترف):
        \"\"\"
        
        humanized = await self.ai.generate_response(robotic_response, system_prompt)
        return humanized.strip()

    def _ensure_table_exists(self):
        \"\"\"إنشاء جدول الأمثلة التعليمية لو مش موجود\"\"\"
        with get_db_cursor() as cur:
            if not cur: return
            cur.execute(\"\"\"
                CREATE TABLE IF NOT EXISTS bot_training_samples (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    question TEXT,
                    robotic_response TEXT,
                    humanized_response TEXT,
                    category VARCHAR(100) DEFAULT 'general',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            \"\"\")

    async def train_on_questions(self, questions_list):
        \"\"\"دورة تدريبية كاملة على مجموعة أسئلة\"\"\"
        self._ensure_table_exists()
        
        logger.info(f\" Starting Training Loop for {len(questions_list)} questions...\")
        
        for q in questions_list:
            logger.info(f\" Question: {q}\")
            
            # 1. الحصول على الرد الآلي (نظامنا الحالي)
            # ملحوظة: هنا بنفترض إننا بنكلم محرك الـ AI مباشرة أو عبر الويب هوك
            robotic_resp = await ai_engine.generate_response(q, \"TRAINING_MODE\")
            logger.info(f\"🤖 Bot (Raw): {robotic_resp[:50]}...\")
            
            # 2. تحويله لبشري
            human_resp = await self.humanize_bot_response(q, robotic_resp)
            logger.info(f\"✨ Yasmine (Human): {human_resp[:50]}...\")
            
            # 3. حفظ في الداتابيز كـ Gold Standard
            with get_db_cursor() as cur:
                cur.execute(\"\"\"
                    INSERT INTO bot_training_samples (question, robotic_response, humanized_response)
                    VALUES (%s, %s, %s)
                \"\"\", (q, robotic_resp, human_resp))
            
            logger.info(\" Saved to Knowledge Base\")
            await asyncio.sleep(1) # لعدم إجهاد الـ API



    async def train_on_weak_interactions(self, limit=10):
        \"\"\"
        تدريب على محادثات حقيقية كان فيها الـ Intent غير مؤكد
        \"\"\"
        logger.info(\"🔍 Scanning for weak interactions in DB...\")
        with get_db_cursor() as cur:
            if not cur: return
            # جلب الرسائل التي لم يفهمها البوت جيداً (مثلاً اللي رد عليها بـ Fallback)
            # هذه ميزة متقدمة سنفعلها لاحقاً بالتكامل مع جدول الرسائل
            pass

    async def run_nightly_training(self):
        \"\"\"المهمة الليلية المجدولة\"\"\"
        logger.info(\"🌙 Starting Nightly Brain Training...\")
        await self.train_on_questions(TRAINING_QUESTIONS)
        # await self.train_on_weak_interactions()
        logger.info(\"✅ Training Complete.\")

async def main():
    trainer = BrainTrainer()
    # تشغيل الدورة الليلية (Nightly Loop)
    await trainer.run_nightly_training()

if __name__ == \"__main__\":
    asyncio.run(main())

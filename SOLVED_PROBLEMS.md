# Solved Problems Log

## 1. Empty Response for Audio Messages (N8N Workflow)

**Date:** 2026-02-11
**Status:** ✅ Solved

### Issue

When a user sends an audio message, the AI bot in N8N responds with a generic fallback message ("عايز تعرف عن إيه بالظبط؟") instead of transcribing the audio and answering based on its content.

### Root Cause

1. **Payload Mismatch:** The Python backend was forwarding data inside a `body` object, while the N8N AI Agent prompt was looking for `$json.message` (which was undefined).
2. **Data Structure Mismatch:** The Google Gemini node (used for transcription) outputs data in a nested structure: `content.parts[0].text`. The AI Agent prompt was attempting to read from `json.text`, which did not exist on that node's output.

### Solution (Surgical Fix)

Updated the AI Agent node's prompt to use the correct data paths:

- **Audio path:** Changed `$("Transcribe a recording2").first().json.text` to `$("Transcribe a recording2").first().json.content.parts[0].text`.
- **Text path:** Changed `$json.message` to `$json.body.message` to align with the backend's forwarding structure.

---

## 2. Double Bot Replies (Python vs N8N)

**Date:** 2026-02-11
**Status:** ✅ Solved

### Issue

The bot was sending two replies: one long/robotic message from the Python backend and one from N8N.

### Root Cause

Both the Python backend and N8N were configured to process the same webhook and generate AI responses independently.

### Solution

Implemented a "**One Brain**" architecture:

1. Disabled AI response generation in the Python backend (`webhook_handler.py`).
2. Enabled active forwarding to N8N as the primary brain.
3. Updated `deploy.ps1` to ensure `trips_db.json` and `docker-compose.yaml` are correctly synced to the server with proper volumes.

---

## 3. Gemini API Connection Failure (Proxy & API Key)

**Date:** 2026-02-12
**Status:** ✅ Solved

### Issue

The system failed to connect to Gemini AI through the Antigravity Proxy, returning "API key not valid" errors and "Handshake failed" SSL errors when using the old SDK.

### Root Cause

1. **Invalid API Key:** The key in `الـ Secrets الكاملة.txt` starting with `AIzaSyA9Tu...` was no longer valid.
2. **SDK Deprecation:** The `google.generativeai` package is deprecated. Switching to the new `google-genai` SDK required a different approach for proxy configuration.
3. **Configuration Endpoint Mismatch:** The initial attempt to set the proxy endpoint via `client_options` failed in the new SDK because it expects either a direct `api_endpoint` parameter in the client or a specific environment variable.

### Solution (Surgical Fix)

1. **Key Replacement:** Identified and verified a working API key: `AIzaSyDBrn8vJ3k1Xu86VhdNHSse9ybbJyxDG2g`.
2. **Environment Configuration:** Set `os.environ["GOOGLE_GENAI_API_ENDPOINT"] = "http://127.0.0.1:8045"` to route all SDK traffic through the local proxy.
3. **Client Optimization:** Initialized the client using:
   ```python
   client = genai.Client(api_key="...", vertex=False)
   ```
   ```

   ```
4. **Verification:** Success confirmed via `test_gemini_via_proxy_stable.py` with a 200 OK response from the proxy and a valid AI response.

---

## 4. Guest Trial Authentication Loop (SAAS-017)

**Date:** 2026-02-22
**Status:** ✅ Solved

### Issue

Users clicking "Continue As Guest" were granted local UI access, but subsequent API calls failed with `401 Unauthorized` because they lacked a valid JWT. The `Dio` interceptor interpreted this as an expired session, forcing a logout loop back to the activation screen.

### Root Cause & Pipeline Analysis

The frontend (`auth_provider.dart`) was faking the session locally without informing the backend. The backend APIs inherently expect a `user_id` and `instance_name` for isolated queries (as per Rule 11).

### Solution (Surgical Fix)

1. **Backend (`routers/license.py`):** Created a `/guest` endpoint that generates a real JWT token with a `guest` role and a null-equivalent UUID (`00000000-0000-0000-0000-000000000000`) for the `user_id` to bypass PostgreSQL type casting errors while maintaining query isolation.
2. **Frontend State (`auth_provider.dart`):** Updated `AuthGuest` to hold the `token`. The `continueAsGuest` method now makes a real HTTP request to fetch and save this token.
3. **Network Interceptor (`dio_provider.dart`):** Updated to explicitly inject the `AuthGuest` token into the `Authorization` header, and resolved a race condition by `await`ing the Future of `authProvider`.

---

## 5. مشكلة ظهور الكيور ار كود (404 WhatsApp QR Failure)

**التاريخ:** 2026-03-14
**الحالة:** ✅ تم الحل

### المشكلة

تعطل ظهور رمز الـ QR الخاص بربط الواتساب في واجهة المستخدم، مع ظهور أخطاء 404 أو تعليق الـ Dialogue الخاص بالربط بدون تحديث للبيانات.

### الأسباب الجذرية

1.  **عدم توافق هيكلية البيانات (Data Mismatch):** كان الـ Backend يرسل البيانات بتنسيق مباشر، بينما كان الـ Frontend (Flutter) يتوقع تغليفاً معيناً (`{"success": true, "data": {...}}`).
2.  **غياب آلية تصفية الجلسات (Missing Reset Logic):** لم يكن هناك مسار (Endpoint) لعمل تسجبل خروج إجباري أو إعادة تهيئة للجلسة العالقة (Stuck Session) في جسر Baileys.
3.  **ضعف في واجهة المستخدم (UI Feedback):** غياب أزرار التحديث (Refresh) والمسح الإجباري (Forced Reset) جعل من الصعب على المستخدم تدارك حالات انتهاء صلاحية الـ QR أو الأخطاء المؤقتة.

### الحل (Surgical Fix)

1.  **توحيد استجابة الـ API:** تعديل ملف `backend/routers/evolution.py` لضمان إرجاع استجابة موحدة للـ QR والـ Status تتوافق مع توقعات تطبيق Flutter.
2.  **إضافة مسارات التحكم:**
    *   إنشاء مسار `/logout` لتنظيف الجلسة برمجياً.
    *   إنشاء مسار `/pairing-code` لطلب كود الربط بالهاتف مباشرة.
3.  **تطوير واجهة الربط (PairingDialog.dart):**
    *   إضافة زر **REFRESH** لتحديث الـ QR يدوياً.
    *   إضافة زر **FORCED RESET** لمسح الجلسة القديمة وإعادة البدء.
    *   إضافة معالجة لحالة "المتصل بالفعل" (ALREADY_CONNECTED) لإبلاغ المستخدم بدلاً من عرض QR فارغ.
4.  **تحسين الاستقرار:** إضافة تأخير زمني (3 ثوانٍ) بعد المسح للسماح للجسر (Bridge) بإعادة التشغيل قبل طلب QR جديد.

---

## 6. عدم استجابة البوت وتوقف تحويل الرسائل لـ N8N

**التاريخ:** 2026-03-14
**الحالة:** ✅ تم الحل

### المشكلة

عند إرسال رسالة من واتساب (هاتف المستخدم)، يستقبلها جسر `Baileys` بنجاح ولكن البوت لا يرد ولا يتم تحويل أي بيانات إلى `N8N` ليعمل، مما يؤدي لتوقف تدفق المحادثة الذكية.

### الأسباب الجذرية

1. **تخطي إعدادات البيئة (Env Override):** في ملف `docker-compose.yml`، كان هناك إعداد للـ `DATABASE_URL` خاص بالـ `g777-backend` يوجهه إلى قاعدة البيانات الخاطئة فتوقف الكود.
2. **Crash & Halt:** عندما استقبل الـ Backend رسالة حدث الـ Crash. تم حله في البداية وتم تمرير الرسالة.
3. **تغير صيغة الـ Payload للجسور:** في N8N، كانت عقدة "إرسال رسالة" (`Send Text1`) مصممة لترسل الطلبات بصيغة جسر "Evolution API" القديم `{ "number": "...", "text": "..." }`. بينما جسر `Baileys` الجديد يطلب البيانات بصيغة `{ "phone": "...", "message": "..." }`. مما أدى لرفض جسر `Baileys` للعملية بخطأ `400 Bad Request`.

### الحل (Surgical Fix)

1. **تصحيح مسار قاعدة البيانات:** تمت إزالة السطر الذي يفرض `DATABASE_URL` يدوياً على `g777-backend` في ملف `docker-compose.yml` لتصليح استقبال الرسائل.
2. **تحديث سير عمل N8N برمجيًا (DB Migration):** قمت بالدخول على قواعد بيانات N8N المحلية والمخبرية (`database.sqlite`) وتحديث المتغيرات في عقدة `Send Text1` لتصبح `phone` بدلاً من `number` و `message` بدلاً من `text` لتتوافق تماماً مع جسر `Baileys`.
3. **ضبط الروابط:** قمت بضبط الروابط الداخلية (Localhost) في بيئة العمل لتتوافق مع Docker و host.
4. **تفعيل إعداد المحاولة (Retry):** تفعيل إعدادات إعادة المحاولة في عقد الـ Memory لتجنب أخطاء الاتصال العابرة مع Supabase.

**ملاحظة الاختبار:** لتطبيق التعديلات التي قمت بها في قاعدة بيانات N8N بشكل مباشر، **يرجى تحديث الصفحة (Refresh)** الخاصة بسير العمل في متصفحك لظهور التغييرات البرمجية، ثم يمكنك إرسال الرسالة وسيرد البوت فوراً.

5. **حل تعارض النسخ المزدوجة (Dual N8N Instances):** تم اكتشاف أنك تقوم بتشغيل نسختين من N8N في وقت واحد؛ واحدة Docker على المنفذ `5680` والأخرى محلياً في التيرمنال على `5678`. كان الـ Backend يقوم بتوجيه الرسائل للنسخة الخاصة بـ Docker، بينما أنت تنتظر الرسالة في المتصفح الذي يفتح نسخة التيرمنال. تم تعديل ملف `.env` (`N8N_WEBHOOK_URL=http://172.19.0.1:5678...`) لتوجيه الأحداث برمجياً مباشرة عبر جسر شبكة الـ Docker إلى الـ Terminal الخاص بك.

---

## سجل العمليات الجراحية - جلسة 2026-03-14 (Post-Mortem Sprint #3)

> **الهدف:** تصليح مسار الرسائل الكامل من الواتساب -> Baileys -> Backend -> N8N -> AI -> رد تلقائي.

---

### المشكلة 6: Split-Brain N8N (نسختان تعملان معاً)

**المشكلة:** تشغيل n8n محلياً في التيرمنال على المنفذ `5678` في نفس الوقت مع نسخة Docker على المنفذ `5680`. الباك إند كان يرسل الـ Webhooks للنسخة الداخلية بينما المستخدم يراقب النسخة المحلية.

**السبب الجذري:** عدم توحيد بيئة التشغيل — وجود نسختين يسبب تضارباً في استقبال الـ Webhooks وصعوبة في تتبع التنفيذ.

**الحل الهندسي (Architectural Decision):**
- إغلاق النسخة المحلية وتوحيد n8n داخل Docker بالكامل.
- ربط الـ Volume بـ `~/.n8n:/home/node/.n8n` للحفاظ على الـ Workflows.
- تغيير المنفذ من `5680:5678` إلى `5678:5678` للاتساق.
- إضافة `user: "1000:1000"` لضمان صلاحيات الكتابة على الـ Volume.

---

### المشكلة 7: TLS Timeout — N8N يتصل بـ Supabase مباشرة

**الخطأ:** `ECONNRESET — Client network socket disconnected before secure TLS connection was established`

**السبب الجذري:** عقدتا `Get Memory` و `Save Memory` كانتا تكلمان `https://supabase.co` مباشرة من داخل Docker — اتصال خارجي يفشل بسبب إشكاليات SSL/IPv6 في شبكة Bridge. كما أن هذا يكسر مبدأ Single Source of Truth ويعرض مفاتيح Supabase للخطر داخل n8n.

**الحل المعماري (Internal Proxy Pattern):**

1. **إنشاء Memory Router** (`backend/routers/memory.py`):
   - `GET /memory?phone=xxx` — يجلب ذكريات العميل من Supabase عبر DatabaseManager.
   - `POST /memory` — يحفظ ذاكرة جديدة `{phone, intent, fact}`.
2. **تسجيل الـ Router** في `api/router_registry.py` تحت prefix `/memory`.
3. **إضافة `/memory` لـ exempt_paths** في `core/config.py`.
4. **تحديث middleware** في `core/middleware.py` من exact match إلى `startswith`.
5. **تحديث قاعدة بيانات N8N** برمجياً: Supabase URL -> `http://g777_backend:8000/memory`.

---

### المشكلة 8: 404 Not Found — مسار Evolution API خاطئ في عقدة الإرسال

**الخطأ:** `404 — Cannot POST /message/sendText`

**السبب الجذري:** عقدة `Send Text1` كانت تستخدم مسار Evolution API القديم `/message/sendText` بينما جسر Baileys يعمل على `/send` فقط.

**الحل الجراحي:** تحديث URL في قاعدة بيانات N8N برمجياً من `/message/sendText` الى `/send`.

---

### Architecture Map v3.0 (الحالة الصحيحة)

```
WhatsApp -> Baileys Bridge (baileys-bridge:3000)
         -> POST /webhook/whatsapp -> g777_backend (g777-backend:8000)
         -> POST g777_n8n:5678/webhook/{uuid} -> N8N Workflow
            - GET  g777_backend:8000/memory?phone=...   [Get Memory]
            - AI Agent (Gemini)
            - POST g777_backend:8000/memory             [Save Memory]
            - POST baileys-bridge:3000/send             [Send Reply]
         -> WhatsApp [AI Reply Delivered]
```

### قواعد المعمارية (للمحررين المستقبليين)

| القاعدة | التفاصيل |
|---|---|
| لا اتصال خارجي من n8n | n8n يكلم g777_backend فقط — الباك إند يكلم Supabase |
| لا نسختين من نفس الخدمة | Docker او محلي — ليس كلاهما |
| مسار الإرسال الصحيح | http://baileys-bridge:3000/send بـ phone + message |
| مسار الذاكرة الصحيح | http://g777_backend:8000/memory بـ phone + intent + fact |
| مسار الـ Webhook | http://g777_n8n:5678/webhook/{uuid} — داخلي بالكامل |

---

## Sprint #4 — Video Support & RAG Intelligence (2026-03-14)

### الميزة المضافة 1: دعم رسائل الفيديو في N8N Workflow

**المشكلة:** عقدة `Switch1` كانت تعالج فرعين فقط (Audio, Image) بدون أي معالجة لرسائل الفيديو، التي تضيع بصمت.

**الحل الهندسي (Video Pipeline):**

أضفنا فرعاً رابعاً للـ Switch1 يكشف `videoMessage.url`، متصلاً بـ Pipeline كامل:

```
Switch1[Video]
  --> Get BaseVideo  (POST g777_backend:8000 — يجلب base64 للفيديو)
  --> Convert to File4  (قلب base64 -> binary)
  --> Analyze Video1  (Gemini 2.5 Flash — resource: video, inputType: binary)
  --> Get Memory (Addon)1  (يكمل في الـ Pipeline العادي)
```

**المكونات المضافة:**
- `Get BaseVideo` — نفس `Get Base1` لكن على موضع Y مختلف (1632).
- `Convert to File4` — convertToFile node لتحويل base64.
- `Analyze Video1` — `@n8n/n8n-nodes-langchain.googleGemini` بـ resource: video.

**التحديثات المتعلقة:**
- `Format Context (Addon)1`: أضفنا `Analyze Video1` لقائمة الـ nodes التي يحاول الكود استعادة البيانات منها.
- `AI Agent1`: تعبير النص يشمل الآن output من `Analyze Video1`.
- `Extract Intent (Addon)1`: تحسين استخراج الـ phone و userMessage لتشمل حالة الفيديو.

---

### الميزة المضافة 2: RAG Intelligence — الذاكرة في قلب الـ Prompt

**المبدأ:** البوت لم يعد مجرد "ساعي بريد" — هو الآن يستخدم ذاكرة العميل كـ Context للـ AI Agent.

**الـ Pipeline الجديد المكتمل:**

```
Webhook -> Not from me -> Switch1 (Text/Audio/Image/Video)
  -> [media nodes] -> Get Memory (Addon)1
  -> Format Context (تجميع الذاكرة + الرسالة)
  -> AI Agent1 (Gemini + system prompt + memory context)
  -> Loop Over Items -> Extract Intent
  -> Save Memory (Addon)1 (يحفظ التفاعل الجديد)
  -> Wait -> Send Text
```

**قاعدة بيانات الذاكرة:** `customer_memory` تحتوي: phone, intent, fact, created_at.

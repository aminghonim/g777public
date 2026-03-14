# حلول المشكلات التقنية (Issue Resolution Log)

هذا الملف يسجل الألغاز التقنية التي تم حلها لضمان عدم تكرار الأخطاء وتوثيق المعرفة.

---

## [n8n/Backend] لغز الـ 401 (Unauthorized Access)

- **التاريخ:** 2026-03-14
- **المشكلة:** عقد n8n (صوت/فيديو) كانت تفشل في تحميل الميديا لأن الطلب كان يمر عبر `g777_backend:8000` الذي يفرض حماية (Clerk Middleware).
- **السبب الجذري:** محاولة استخدام الباك إند كبروكسي للميديا الداخلية بدون تمرير الـ Token المناسب.
- **الحل الهندسي:** **Bypassing the Backend**. تم الربط المباشر بين n8n وحاوية الجسر (`baileys_bridge:3000`) لفك التشفير داخلياً بدون الحاجة لتعقيدات الأمان.

---

## [Baileys Bridge] لغز الـ 404 (Missing /download Endpoint)

- **التاريخ:** 2026-03-14
- **المشكلة:** حاوية الجسر لم تكن تتعرف على أمر التحميل؛ كانت مبرمجة للإرسال فقط.
- **السبب الجذري:** نقص في تعريف الـ Endpoints الخاصة بفك التشفير في تطبيق الـ Node.js.
- **الحل الهندسي:** **Surgical Code Injection**. حقن كود جديد في `server.js` يستخدم مكتبة Baileys الأصلية لفك تشفير المحتوى وإرجاعه كـ Base64 لـ n8n.

---

## [n8n/Gemini] لغز موديل Veo (Model Mismatch Error)

- **التاريخ:** 2026-03-14
- **المشكلة:** عقدة Gemini في n8n كانت تطلب موديل **Veo** (المتخصص في توليد الفيديو) بدلاً من تحليل الفيديو المرسل.
- **السبب الجذري:** ضبط نوع العملية (Operation) في n8n على "Generate Video" بدلاً من "Multimodal Chat".
- **الحل الهندسي (Task Redefinition):**
  3. **Task Redefinition**: Changed the Gemini node "Operation" in n8n to **Multimodal Chat** (or **Analyze**). Set **Input Type** to **Binary File** to pass the decrypted media buffer directly to the model.
4. **Quoted Media Extractors**: Fixed the issue where media sent as a reply (quoted) was not being detected by adding conditional logic in n8n Switch nodes and smart extraction in the Baileys Bridge.
في الخطوة السابقة.
- **الموديل المستخدم:** Gemini 2.5 Flash (يعامل الفيديو كـ Visual Inputs).

---

## [n8n/WhatsApp] لغز الرد المتداخل (Quoted Media Recovery)

- **التاريخ:** 2026-03-14
- **المشكلة:** البوت لا يستجيب عند الرد (Reply) على فيديو أو صورة؛ عقدة الـ Switch في n8n لا تجد مسار الميديا.
- **السبب الجذري:** واتساب يغير هيكل الرسالة عند الرد؛ يضع الميديا داخل `extendedTextMessage.contextInfo.quotedMessage` بدلاً من المسار المباشر.
- **الحل النهائي:** 
  1. **تحديث العقد (Switch):** إضافة منطق `||` (OR) في n8n لفحص المسار المباشر والمقتبس.
  2. **حقن ذكي (Bridge Injection):** تعديل `/download` في `server.js` للتعرف تلقائياً على الرسائل المقتبسة واستخراج الميديا منها قبل فك التشفير.
- **القاعدة الذهبية:** دائماً ضع فرع الميديا (Image/Video) قبل فرع النص في الـ Switch.

---

**آخر تحديث:** 2026-03-14 (Quoted Media Fix)
**المسؤول:** أنتجرافتي (Senior System Engineer)

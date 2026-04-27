# 🛡️ سجل الحلول التقنية (Troubleshooting Knowledge Base)

> **تنبيه للنظام:** قبل طرح أي حل جديد، راجع هذا الملف أولاً.
> إذا وجدت المشكلة هنا، طبق الحل المسجل فوراً بدون تخمين.

---

## [Docker] خطأ `KeyError: 'ContainerConfig'`
- **التاريخ:** 2026-01-20
- **المشكلة:** `KeyError: 'ContainerConfig'` عند تشغيل `docker-compose up`.
- **السبب الجذري:** استخدام `docker-compose` (النسخة القديمة المبنية على Python v1.29.2) مع إصدار Docker Engine حديث (v28+) لا يرسل بيانات `ContainerConfig` في الـ API.
- **الحل النهائي:** استبدال الأداة القديمة بـ Docker Compose V2 (المبني على Go).
- **طريقة التثبيت (Ubuntu 22.04 مع docker.io):**
  ```bash
  # تحميل Docker Compose V2 مباشرة
  sudo curl -L 'https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-x86_64' -o /usr/local/bin/docker-v2
  sudo chmod +x /usr/local/bin/docker-v2
  ```
- **الأمر الناجح:**
  ```bash
  sudo /usr/local/bin/docker-v2 up -d
  ```
- **ملاحظة:** لا تستخدم `docker-compose` (بالشرطة) أبداً على هذا السيرفر.

---

## [Docker] تعارض أسماء الحاويات (Container Name Conflict)
- **التاريخ:** 2026-01-20
- **### المشكلة الثالثة: خطأ 'coroutine' و 'NoneType' (التحديث النهائي - يناير 2026)
*   **الخلفية:** تعذر قراءة المحتوى وخطأ `bytes-like object required, not coroutine` بالإضافة لفقدان السمة `name`.
*   **الحل الجذري (التحصين):** 
    1. إنشاء مديول `ui/utils.py` يحتوي على دالة `get_safe_upload_data` الموحدة.
    2. الدالة تستخدم `await` ذكي مع فحص `asyncio.iscoroutinefunction`.
    3. التعامل مع `e.file.filename` كبديل لـ `e.name` المفقود في بعض النسخ.
    4. **القاعدة:** يُمنع كتابة منطق رفع يدوي في أي صفحة؛ يجب استدعاء المديول الموحد فقط.
- **الأمر التشخيصي:**
  ```bash
  sudo docker ps -a
  ```
- **الأمر العلاجي:**
  ```bash
  sudo docker rm -f <container_id_or_name>
  ```
- **ملاحظة:** استخدم الـ ID الكامل للحاوية إذا كان الاسم معقداً.

---

## [Azure VM] منطقة Azure غير متوفرة (SKU Not Available)
- **التاريخ:** 2026-01-20
- **المشكلة:** `SkuNotAvailable: The requested VM size 'Standard_B2s' is currently not available in location 'SwedenCentral'`.
- **السبب الجذري:** Azure تحجز موارد معينة لعملاء آخرين أو للصيانة في مناطق محددة.
- **الحل النهائي:** تغيير الموقع (Location) في أمر الإنشاء.
- **المناطق البديلة المستقرة:**
  - `northeurope` (أيرلندا)
  - `westeurope` (هولندا)
  - `eastus` (الولايات المتحدة)
- **الأمر المعدل:**
  ```powershell
  .\launch_g777_vm.ps1 -Location "northeurope" ...
  ```

---

## [Baileys/WhatsApp] الحفاظ على جلسة الربط
- **التاريخ:** 2026-01-20
- **المعلومة الحيوية:** جلسة ربط الواتساب محفوظة في مجلد `auth_info` داخل حاوية `baileys-service`.
- **المسار على السيرفر:** `/home/azureuser/g777/baileys-service/auth_info/`
- **الملف الأهم:** `creds.json`
- **القاعدة الذهبية:** أي عملية تعديل أو إعادة تشغيل يجب أن تحافظ على هذا المجلد (Docker Volumes).
- **التحقق من سلامة الجلسة:**
  ```bash
  ls -la /home/azureuser/g777/baileys-service/auth_info/
  # يجب أن يظهر creds.json وملفات session-*.json
  ```

---

## [NeonDB] انقطاع الاتصال المفاجئ (SSL Unexpected Close)
- **التاريخ:** 2026-01-20
- **المشكلة:** `psycopg2.OperationalError: SSL connection has been closed unexpectedly`.
- **السبب الجذري:** Azure Load Balancer يقطع الاتصالات الخاملة (Idle Connections) بعد 4 دقائق.
- **الحل النهائي:** إضافة إعدادات `keepalives` في رابط الاتصال.
- **الكود (في ملف .env):**
  ```
  DATABASE_URL=postgresql://...?sslmode=require&keepalives=1&keepalives_idle=30
  ```

---

## [PowerShell] أوامر curl لا تعمل
- **التاريخ:** 2026-01-20
- **المشكلة:** `curl -I` أو `curl --connect-timeout` تعطي أخطاء غريبة في PowerShell.
- **السبب الجذري:** في Windows PowerShell، `curl` هو alias لـ `Invoke-WebRequest` وليس الـ curl الحقيقي.
- **الحل النهائي:** استخدم Python لاختبار الـ HTTP بدلاً من curl.
- **الأمر البديل:**
  ```powershell
  python -c "import requests; print(requests.get('http://example.com').status_code)"
  ```

---

## [Azure VM] فشل ظهور الـ QR Code (Evolution API)
- **التاريخ:** 2026-01-22 (محدث)
- **المشكلة:** عدم ظهور الـ QR Code وحالة الاتصال `connecting` أو `close`.
- **الأعراض:** 
  - حالة الاتصال: `connecting` (عالقة) أو `close` (مفصولة).
  - الـ `disconnectionAt` يظهر تاريخ قديم.
  - البوت لا يستجيب للرسائل.
- **السبب الجذري:**
  1. الجلسة اتفصلت (يدوياً أو بسبب انقطاع) ومحتاجة إعادة ربط.
  2. ملفات الجلسة القديمة لازم تتمسح قبل التوليد الجديد.
- **الحل النهائي (Evolution API على Port 8080):**
  
  **الخطوة 1: فحص حالة الاتصال**
  ```bash
  curl -H "apikey: antigravity_secret_key_2024" \
    http://51.12.91.34:8080/instance/connectionState/SENDER
  ```
  
  **الخطوة 2: لو الحالة `close` أو `connecting` - عمل Logout ثم Connect**
  ```bash
  # Logout (مسح الجلسة القديمة)
  curl -X DELETE -H "apikey: antigravity_secret_key_2024" \
    http://51.12.91.34:8080/instance/logout/SENDER
  
  # Connect (توليد QR جديد)
  curl -H "apikey: antigravity_secret_key_2024" \
    http://51.12.91.34:8080/instance/connect/SENDER
  ```
  
  **الخطوة 3: حفظ الـ QR Code كصورة (Python)**
  ```python
  import requests, base64
  r = requests.get('http://51.12.91.34:8080/instance/connect/SENDER', 
      headers={'apikey': 'antigravity_secret_key_2024'})
  b64 = r.json()['base64'].split(',')[1]
  with open('qr_code.png', 'wb') as f:
      f.write(base64.b64decode(b64))
  ```

- **التحقق من النجاح:**
  ```bash
  # يجب أن يظهر state: open
  curl -H "apikey: antigravity_secret_key_2024" \
    http://51.12.91.34:8080/instance/connectionState/SENDER
  ```
- **القاعدة الذهبية:** إذا كانت الحالة `connecting` لأكثر من 30 ثانية، نفذ Logout ثم Connect.

---

## [Config] خلط بين Port 3000 (Baileys) و Port 8080 (Evolution API)
- **التاريخ:** 2026-01-22
- **المشكلة:** البرنامج يظهر "Disconnected" و "QR Code Not Available" رغم أن السيرفر يعمل.
- **الأعراض:**
  - صفحة الربط تظهر "Service Issue" و "QR Code Not Available".
  - الـ Refresh لا يجدي نفعاً.
  - لكن عند اختبار الـ API يدوياً من الترمينال على Port 8080، كل شيء يعمل!
- **السبب الجذري:**
  - ملف `.env` كان يحتوي على:
    - `BAILEYS_API_URL=http://51.12.91.34:3000` ← خدمة قديمة
    - `EVOLUTION_API_URL=http://51.12.91.34:8080` ← الخدمة الفعلية
  - الكود في `cloud_service.py` كان يقرأ `BAILEYS_API_URL` (Port 3000) بدلاً من `EVOLUTION_API_URL` (Port 8080).
- **الحل النهائي:**
  1. تحديث `cloud_service.py` ليقرأ `EVOLUTION_API_URL` كإعداد رئيسي.
  2. تحديث الـ endpoints لتتوافق مع Evolution API v2:
     - فحص الاتصال: `GET /instance/connectionState/{instance}`
     - جلب QR: `GET /instance/connect/{instance}`
     - إرسال رسالة: `POST /message/sendText/{instance}`
     - قطع الاتصال: `DELETE /instance/logout/{instance}`
  3. إضافة الـ `apikey` header في كل الطلبات.
- **الملفات المعدلة:**
  - `backend/cloud_service.py`
- **القاعدة الذهبية:** دائماً استخدم Evolution API على Port 8080. الخدمة على Port 3000 (Baileys Service) هي خدمة مساعدة فقط.
- **✅ تم التحقق:** 2026-01-22 12:58 - الربط تم بنجاح والاتصال مستقر.

---

## [Config] خطأ في عنوان n8n (Local vs Cloud)
- **التاريخ:** 2026-01-22
- **المشكلة:** فشل في ربط Webhook وتلقي رسالة "No workspace here" عند استخدام رابط n8n Cloud.
- **السبب الجذري:** 
  - كنا نعتقد أن n8n مستضاف سحابياً (Cloud).
  - الحقيقة: n8n مثبت ومستضاف محلياً على السيرفر نفسه (Azure VM) على المنفذ `5678`.
- **الحل النهائي:**
  - استخدام رابط الويب هوك الداخلي: `http://51.12.91.34:5678/webhook/whatsapp`
  - تم تحديث إعدادات Evolution API لتوجيه الرسائل لهذا الرابط المحلي.
- **✅ تم التحقق:** 2026-01-22 13:18 - تم ربط الويب هوك بنجاح (Status 201).

---


---

## [UI/UX] التحديث التلقائي (Auto-Refresh) يمسح QR Code
- **التاريخ:** 2026-01-23
- **المشكلة:** صفحة الربط في البرنامج تقوم بعمل Refresh كل 10 ثواني، مما يؤدي إلى إنشاء QR جديد ومسح القديم قبل أن يمسحه المستخدم.
- **الأعراض:**
  - الـ QR Code يظهر ويختفي بسرعة.
  - رسائل في الـ Log: `Session stale, doing logout first...` تتكرر كل 10 ثواني.
  - المستخدم لا يستطيع الربط أبدياً.
- **السبب الجذري:**
  - استخدام `ui.timer(10, refresh_all)` في واجهة المستخدم.
  - دالة التحديث كانت تقوم بعمل `Logout` تلقائي قبل طلب `QR` جديد.
- **الحل النهائي:**
  - تعطيل التحديث التلقائي تماماً.
  - الاكتفاء بالتحديث عند فتح الصفحة فقط (`once=True`).
  - إضافة زر "Refresh Manually" للمستخدم.
- **الملفات المعدلة:**
  - `ui/pairing_page.py`
- **القاعدة الذهبية:** لا تستخدم Auto-Refresh مع عمليات تتطلب تفاعل مستخدم طويل (مثل مسح QR).

---

## [n8n] فشل استخراج البيانات (Webhook Parser)
- **التاريخ:** 2026-01-23
- **المشكلة:** الرسائل تصل إلى n8n لكن يتم تجاهلها أو تظهر كبيانات فارغة.
- **الأعراض:**
  - الـ Webhook يظهر باللون الأخضر (نجاح).
  - العقد التالية (Parser, AI) تظهر باللون الرمادي (توقف) أو تخرج بيانات فارغة.
- **السبب الجذري:**
  - اختلاف هيكل البيانات (JSON Structure) القادم من Evolution API.
  - الكود القديم كان يبحث في `body.key` بينما البيانات كانت في `body.data.key`.
- **الحل النهائي:**
  - كتابة "Universal Messsage Parser" في n8n.
  - الكود الجديد يبحث عن البيانات في جميع المسارات المحتملة (`body.data`, `body`, `data`, `root`).
- **الكود المصحح:**
  ```javascript
  const body = incoming.body?.data || incoming.data || incoming.body || incoming;
  ```
- **الملفات المعدلة:**
  - n8n Workflow (Node: "Message Parser")

---

## [API] استخدام Endpoints خاطئة (Health Check)
- **التاريخ:** 2026-01-23
- **المشكلة:** رسائل خطأ `404 Not Found` عند فحص حالة السيرفر، رغم أنه يعمل.
- **الأعراض:**
  - Postman يعطي: `"message": ["Cannot GET /health"]`.
  - الاعتقاد الخاطئ بأن السيرفر معطل.
- **السبب الجذري:**
  - افتراض وجود Endpoint `/health` (شائع في Baileys) بينما Evolution API يستخدم `/ping` أو `/instance/connectionState`.
- **الحل النهائي:**
  - استخدام الـ Endpoints الرسمية لـ Evolution v2:
    - للفحص: `/ping`
    - للاتصال: `/instance/connectionState/{name}`
  - التأكد دائماً من إرسال `apikey` في الـ Header.

---
---

## [Evolution API] Redis مفقود - WhatsApp لا يربط
- **التاريخ:** 2026-01-23
- **المشكلة:** Evolution API يعطي خطأ `redis disconnected` متكرر، ولا يمكن ربط WhatsApp.
- **الأعراض:**
  - حالة الاتصال: `close` أو `connecting` دائماً
  - الـ QR Code يظهر لكن المسح لا يعمل
  - الـ Logs مليانة بـ `ERROR [Redis] redis disconnected`
- **السبب الجذري:**
  - ملف `docker-compose.yaml` الأصلي ما كانش فيه خدمة Redis
  - Evolution API اتشغل بشكل منفصل (مش من docker-compose)
  - Redis كان مفقود تماماً من السيرفر
- **الحل النهائي:**
  - تحديث `docker-compose.yaml` ليشمل Redis + Evolution API + PostgreSQL.
- **القاعدة الذهبية:** Evolution API v2+ **يتطلب Redis** للعمل.
- **✅ تم التحقق:** 2026-01-23 - الربط تم بنجاح.

---
---

## [Evolution API] الجلسة العالقة (Stale Session) تمنع الربط الجديد
- **التاريخ:** 2026-01-23
- **المشكلة:** عند محاولة ربط الواتساب مرة أخرى بعد الخروج، لا يظهر QR Code أو يظهر ولا يعمل.
- **### المشكلة الأولى: الإشعار المعلق (Stuck Notification)
*   **السبب:** استخدام متغيرات عامة (Global/Shared State) للإشعارات وتداخل نطاقات الـ Closure.
*   **الحل:** 
    1. تحويل متغير التنبيه `notif` ليكون **Local Scope** داخل دالة الإرسال.
    2. وضع كود الإرسال بالكامل داخل بلوك `try...finally` لضمان الإغلاق.
    3. استخدام حماية `try...except` داخل الـ `finally` لضمان عدم توقف المسح إذا كان الكائن `None`.

### المشكلة الثانية: نقص أوراق الإكسيل (Sheets Missing)
*   **السبب:** اعتماد `openpyxl` المباشر الذي يفشل في ملفات معينة.
*   **الحل:** تحديث `backend/excel_processor.py` لاستخدام `pd.ExcelFile` مع `engine='openpyxl'` لضمان قراءة كافة الأوراق بنسبة نجاح 100%.
- **الأعراض:**
  - المستخدم يضغط "Link a Device" ويمسح الكود، لكن لا يحدث شيء.
  - السيرفر يرفض الاتصال بسبب وجود ملفات جلسة قديمة لم تُحذف.
- **السبب الجذري:**
  - Evolution API لا يحذف ملفات الجلسة (`creds.json`) تلقائياً عند قطع الاتصال من الموبايل.
  - عند طلب QR جديد، النظام يظن أن الجلسة ما زالت قائمة فيرفض الطلب.
- **الحل النهائي:**
  - تعديل كود `get_evolution_qr` في `cloud_service.py`.
  - المنطق الجديد:
    1. افحص الحالة (`connectionState`).
    2. إذا كانت `close` أو `connecting` (وليست `open`) ← نفذ **Force Logout** فوراً.
    3. انتظر 2 ثانية لضمان حذف الملفات.
    4. اطلب QR Code جديد.
- **الملفات المعدلة:**
  - `backend/cloud_service.py`
- **القاعدة الذهبية:** "نظّف القديم قبل ما تبني الجديد". دائماً تأكد من حذف الجلسة السابقة (`DELETE /logout`) قبل طلب QR جديد.

---

## [Evolution API] الويب هوك لا يصل للـ n8n (Hairpin NAT / Stale Container)
- **التاريخ:** 2026-01-31
- **المشكلة:** الرسائل تصل للواتساب (Evolution API) ولكن n8n لا يشعر بها ولا توجد Executions.
- **الأعراض:**
  - حالة الاتصال: `open`.
  - عند تجربة الويب هوك من خارج السيرفر (Postman) الـ n8n يرد.
  - عند إرسال رسالة حقيقية الصمت التام.
- **السبب الجذري:**
  1. **Hairpin NAT:** الـ Azure VM ترفض خروج الطلب للـ Public IP والرجوع لنفس السيرفر.
  2. **Stale Webhook:** الحاوية (Container) أحياناً تتوقف عن إرسال الطلبات الخارجية وتحتاج إعادة تشغيل.
  3. **Port Mismatch:** خلط بين بورت الباكيند (8081) وبورت n8n الفعلي (5678).
- **الحل النهائي:**
  1. استخدام الويب هوك الداخلي عبر الـ Gateway IP: `http://172.17.0.1:5678/webhook/whatsapp`.
  2. التأكد من ضبط بورت n8n في ملف `.env` على `5678`.
  3. عمل **Restart كلي** لحاوية Evolution API عبر الأمر:
     `sudo docker restart evolution-api`
- **القاعدة الذهبية:** إذا كان الـ Webhook صحيحاً والـ n8n شغال والحالة `open` ومع ذلك لا يوجد رد، **رست الدكر فوراً**.

### [NEW] تحديثات حماية موديول الإرسال (يناير 2026):
1. **رفع الملفات:** تم توحيد المنطق في `ui/utils.py` لمنع أخطاء `AttributeError` و `Coroutine` للأبد.
2. **استقرار الواجهة:** الإشعارات أصبحت `Local Scope` لمنع التعليق، والـ Excel Engine تم تحديثه لـ `Pandas ExcelFile`.

---
**آخر تحديث:** 2026-01-31
**المسؤول:** أنتجرافتي (Senior System Engineer)

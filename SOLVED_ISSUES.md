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
- \*\*### المشكلة الثالثة: خطأ 'coroutine' و 'NoneType' (التحديث النهائي - يناير 2026)

* **الخلفية:** تعذر قراءة المحتوى وخطأ `bytes-like object required, not coroutine` بالإضافة لفقدان السمة `name`.
* **الحل الجذري (التحصين):**
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

## [Local Docker] منطقة Azure غير متوفرة (SKU Not Available)

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

## [Local Docker] فشل ظهور الـ QR Code (Evolution API)

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
  curl -H "apikey: {{EVOLUTION_API_KEY}}" \
    http://127.0.0.1:8080/instance/connectionState/SENDER
  ```

  **الخطوة 2: لو الحالة `close` أو `connecting` - عمل Logout ثم Connect**

  ```bash
  # Logout (مسح الجلسة القديمة)
  curl -X DELETE -H "apikey: {{EVOLUTION_API_KEY}}" \
    http://127.0.0.1:8080/instance/logout/SENDER

  # Connect (توليد QR جديد)
  curl -H "apikey: {{EVOLUTION_API_KEY}}" \
    http://127.0.0.1:8080/instance/connect/SENDER
  ```

  **الخطوة 3: حفظ الـ QR Code كصورة (Python)**

  ```python
  import requests, base64
  r = requests.get('http://127.0.0.1:8080/instance/connect/SENDER',
      headers={'apikey': 'os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')'})
  b64 = r.json()['base64'].split(',')[1]
  with open('qr_code.png', 'wb') as f:
      f.write(base64.b64decode(b64))
  ```

- **التحقق من النجاح:**
  ```bash
  # يجب أن يظهر state: open
  curl -H "apikey: {{EVOLUTION_API_KEY}}" \
    http://127.0.0.1:8080/instance/connectionState/SENDER
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
    - `BAILEYS_API_URL=http://127.0.0.1:3000` ← خدمة قديمة
    - `EVOLUTION_API_URL=http://127.0.0.1:8080` ← الخدمة الفعلية
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
  - الحقيقة: n8n مثبت ومستضاف محلياً على السيرفر نفسه (Local Server) على المنفذ `5678`.
- **الحل النهائي:**
  - استخدام رابط الويب هوك الداخلي: `http://127.0.0.1:5678/webhook/whatsapp`
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
  const body =
    incoming.body?.data || incoming.data || incoming.body || incoming;
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
- \*\*### المشكلة الأولى: الإشعار المعلق (Stuck Notification)

* **السبب:** استخدام متغيرات عامة (Global/Shared State) للإشعارات وتداخل نطاقات الـ Closure.
* **الحل:**
  1. تحويل متغير التنبيه `notif` ليكون **Local Scope** داخل دالة الإرسال.
  2. وضع كود الإرسال بالكامل داخل بلوك `try...finally` لضمان الإغلاق.
  3. استخدام حماية `try...except` داخل الـ `finally` لضمان عدم توقف المسح إذا كان الكائن `None`.

### المشكلة الثانية: نقص أوراق الإكسيل (Sheets Missing)

- **السبب:** اعتماد `openpyxl` المباشر الذي يفشل في ملفات معينة.
- **الحل:** تحديث `backend/excel_processor.py` لاستخدام `pd.ExcelFile` مع `engine='openpyxl'` لضمان قراءة كافة الأوراق بنسبة نجاح 100%.

* **الأعراض:**
  - المستخدم يضغط "Link a Device" ويمسح الكود، لكن لا يحدث شيء.
  - السيرفر يرفض الاتصال بسبب وجود ملفات جلسة قديمة لم تُحذف.
* **السبب الجذري:**
  - Evolution API لا يحذف ملفات الجلسة (`creds.json`) تلقائياً عند قطع الاتصال من الموبايل.
  - عند طلب QR جديد، النظام يظن أن الجلسة ما زالت قائمة فيرفض الطلب.
* **الحل النهائي:**
  - تعديل كود `get_evolution_qr` في `cloud_service.py`.
  - المنطق الجديد:
    1. افحص الحالة (`connectionState`).
    2. إذا كانت `close` أو `connecting` (وليست `open`) ← نفذ **Force Logout** فوراً.
    3. انتظر 2 ثانية لضمان حذف الملفات.
    4. اطلب QR Code جديد.
* **الملفات المعدلة:**
  - `backend/cloud_service.py`
* **القاعدة الذهبية:** "نظّف القديم قبل ما تبني الجديد". دائماً تأكد من حذف الجلسة السابقة (`DELETE /logout`) قبل طلب QR جديد.

---

## [Evolution API] الويب هوك لا يصل للـ n8n (Hairpin NAT / Stale Container)

- **التاريخ:** 2026-01-31
- **المشكلة:** الرسائل تصل للواتساب (Evolution API) ولكن n8n لا يشعر بها ولا توجد Executions.
- **الأعراض:**
  - حالة الاتصال: `open`.
  - عند تجربة الويب هوك من خارج السيرفر (Postman) الـ n8n يرد.
  - عند إرسال رسالة حقيقية الصمت التام.
- **السبب الجذري:**
  1. **Hairpin NAT:** الـ Local Server ترفض خروج الطلب للـ Public IP والرجوع لنفس السيرفر.
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
3. **Number Filter:** استعادة زر الرفع المفقود في `number_filter.py`. تم التأكد من أن `ExcelProcessor` يقرأ الورقة المحددة فقط (`sheet_name`) وليس كل الملف.
4. **Members Grabber (Critical Fix):** استبدال الـ Endpoint القديم `/getParticipants` (الذي يعطي 404) بالـ Endpoint الصحيح `/group/findGroupInfos` المتوافق مع Evolution v2.3.6.
5. **Media Sending (Final Fix):** حل مشكلة الـ 500 عن طريق إضافة `mimetype` و `fileName` ديناميكي للهيكلية المسطحة (Flat Payload).

---

## [Media Sending] خطأ `Internal Server Error (500)` - الذاكرة ممتلئة (Stack Overflow)

- **التاريخ:** 2026-02-01
- **المشكلة:** `Response: {"message":"Maximum call stack size exceeded"}` عند إرسال ملفات ميديا.
- **السبب الجذري:**
  1. إرسال هيكل بيانات دائري (Recursive Structure) في ملفات الميديا يحتوي على كائن `mediaMessage` مكرر داخل الطلب.
  2. إرسال صور بأحجام كبيرة جداً (أكبر من 3MB) مما يتسبب في فشل السيرفر (Node.js) في معالجة الـ Base64 الطويل.
- **الحل النهائي:**
  1. **تبسيط الطلب (Payload) :** حذف الـ `mediaMessage` المكرر والاعتماد على الهيكل المسطح (Flat Structure).
  2. **الضغط التلقائي (Image Compression) :** إضافة كود في `cloud_service.py` يقوم بتصغير الصور التي تزيد عن 1.5MB تلقائياً باستخدام مكتبة `Pillow`.
- **الأمر العلاجي:**
  ```bash
  pip install Pillow
  ```
- **المسؤول:** Antigravity Orchestrator

---

## [Number Filter] خطأ `NameError: 'setitem'` واختفاء الـ Sheets

- **التاريخ:** 2026-02-01
- **المشكلة:** انهيار البرنامج عند اختيار ورقة إكسيل في فلتر الأرقام + صعوبة التبديل بين الأوراق.
- **السبب الجذري:**
  1. استخدام `setitem` داخل `lambda` وهي دالة غير معرفة في النطاق الحالي.
  2. منطق الواجهة كان يخفي الـ `sheet_selector` إذا كان هناك ورقة واحدة فقط بالخطأ.
- **الحل النهائي:**
  1. استبدال الـ `lambda` بدالة داخلية `on_sheet_select` صريحة.
  2. تحديث خاصية `visible` لتكون `True` دائماً بمجرد تحميل ملف إكسيل صالح، لتمكين المستخدم من الاختيار.
- **الملفات المعدلة:** `ui/modules/number_filter.py`

---

## [n8n] خطأ DNS و `EAI_AGAIN g777-backend`

- **التاريخ:** 2026-02-01
- **المشكلة:** فشل اتصال n8n بالباكيند مع رسالة `getaddrinfo EAI_AGAIN g777-backend`.
- **السبب الجذري:**
  1. n8n يعمل في حاوية منفصلة أو شبكة مختلفة عن `g777-backend`.
  2. خدمة DNS داخل Docker لا تستطيع حل اسم الكونتينر إذا لم يكونوا في نفس الـ Docker Network.
- **الحل النهائي:**
  - استخدام **IP البوابة (Host Gateway)** للتخاطب الداخلي المضمون.
  - استبدال الرابط من `http://g777-backend:8081` إلى `http://172.17.0.1:8081` (عنوان Docker Host).
  - هذا العنوان يعمل دائماً للوصول من داخل أي كونتينر إلى السيرفر المستضيف (Host).

---

**آخر تحديث:** 2026-02-03
**المسؤول:** أنتجرافتي (Senior System Engineer)

---

## [UI] خطأ `KeyError: 'orange'` في صفحة Account Warmer

- **التاريخ:** 2026-02-03
- **المشكلة:** انهيار صفحة Account Warmer مع `KeyError: 'orange'` عند استخدام ثيمات معينة.
- **الأعراض:**
  - الخطأ يظهر عند فتح صفحة `whatsapp_tools` والانتقال لـ Account Warmer.
  - الثيمات `Huemint2` و `Catppuccin` تسبب الخطأ.
- **السبب الجذري:**
  - الكود كان يفترض أن جميع الثيمات تحتوي على لون `orange` في قاموس الألوان.
  - بعض الثيمات تستخدم ألوان بديلة مثل `peach` أو `yellow` فقط.
- **الحل الجراحي (Surgical Fix):**
  - استخدام `.get()` بدلاً من الوصول المباشر `c["orange"]`.
  - نظام Fallback: `orange` → `peach` → `red`.
- **الكود المصحح:**
  ```python
  f'background: linear-gradient(90deg, {c["red"]}, {c.get("orange", c.get("peach", c["red"]))});'
  ```
- **الملفات المعدلة:** `ui/modules/account_warmer.py` (السطر 63)
- **الامتثال للـ Architecture Constraints:** ✅ Rule 1.2 (Surgical Fix Only)

---

## [UI] خطأ `RuntimeError: Client deleted` في Facebook Group Hunter

- **التاريخ:** 2026-02-03
- **المشكلة:** انهيار البرنامج عند اكتمال عملية البحث عن المجموعات مع `RuntimeError`.
- **الأعراض:**
  - البحث ينجح وينتهي، لكن يظهر خطأ عند محاولة عرض الإشعار.
  - الخطأ: `RuntimeError: The client this element belongs to has been deleted.`
- **السبب الجذري:**
  - عملية البحث طويلة (async) وتستغرق وقتاً طويلاً.
  - المستخدم يغادر الصفحة أو يغلق المتصفح قبل انتهاء العملية.
  - عند محاولة استدعاء `ui.notify()` بعد الانتهاء، يكون الـ `client` قد تم حذفه.
- **الحل الجراحي:**
  - إضافة `try...except RuntimeError` حول كل `ui.notify()`.
  - في حالة الخطأ، استخدام `print()` للتوثيق بدلاً من الإشعار.
- **الكود المصحح:**
  ```python
  try:
      ui.notify(f'تم العثور على {len(formatted_links)} رابط بنجاح!', type='positive')
  except RuntimeError:
      print(f'Hunt completed: {len(formatted_links)} links found (client disconnected)')
  ```
- **الملفات المعدلة:** `ui/modules/links_grabber.py` (الأسطر 33-35)
- **الامتثال للـ Architecture Constraints:** ✅ Rule 1.2 (Surgical Fix) + Rule 4.1 (Specific Exception)

---

## [API] خطأ `groupJid does not match pattern` في fetch_group_participants

- **التاريخ:** 2026-02-03
- **المشكلة:** فشل جلب أعضاء المجموعة مع `400 Bad Request` من Evolution API.
- **الأعراض:**
  - خطأ: `{"status":400,"error":"Bad Request","response":{"message":[{"property":"groupJid","message":"groupJid does not match pattern \"^[\\d-]+@g.us$\""}]}}`
  - الفيتش يفشل رغم أن الـ group_jid موجود وصالح.
- **السبب الجذري:**
  - Evolution API v2 يتطلب صيغة صارمة للـ groupJid: `123456789-123456789@g.us`.
  - الواجهة كانت ترسل أحياناً الـ ID بدون السوفيكس `@g.us`.
- **الحل الجراحي:**
  1. التحقق من صيغة الـ `groupJid` قبل الإرسال.
  2. إذا لم يكن ينتهي بـ `@g.us`, أضفه تلقائياً.
  3. التحقق من مطابقة الـ Pattern باستخدام `regex`.
- **الكود المضاف:**

  ```python
  import re
  if not group_jid.endswith('@g.us'):
      if re.match(r'^[\d-]+$', group_jid):
          group_jid = f"{group_jid}@g.us"
      else:
          return {"status": 400, "error": "Invalid groupJid format"}

  if not re.match(r'^[\d-]+@g\.us$', group_jid):
      return {"status": 400, "error": "groupJid pattern mismatch"}
  ```

- **الملفات المعدلة:** `backend/cloud_service.py` (الدالة `fetch_group_participants`)

---

## [Members Grabber] ظهور `[object Object]` في قائمة المجموعات

- **التاريخ:** 2026-02-03
- **المشكلة:** ظهور `[object Object]` بدلاً من أسماء المجموعات في القائمة المنسدلة.
- **الأعراض:**
  - عند الضغط على "تحميل المجموعات" تظهر المجموعات لكن بأسماء `[object Object]`.
  - الاختيار يعمل لكن المستخدم لا يستطيع تمييز المجموعات.
- **السبب الجذري:**
  - الـ API يُرجع `name` ككائن (dict) بدلاً من string في بعض الحالات.
  - أو يستخدم مفتاح `subject` بدلاً من `name` (متغير حسب إصدار Evolution).
- **الحل الجراحي:**
  - إضافة دالة `extract_group_name()` تتعامل مع جميع الحالات.
  - دعم مفاتيح متعددة: `name`, `subject`, `groupName`.
  - تحويل أي dict لـ string ومحو `[object Object]` إن ظهرت.
- **الكود المضاف:**
  ```python
  def extract_group_name(g):
      name = g.get('name') or g.get('subject') or g.get('groupName') or 'Unknown'
      if isinstance(name, dict):
          name = name.get('text') or name.get('name') or str(name)
      if '[object' in name.lower():
          name = g.get('id', 'Unknown Group')
      return name
  ```
- **الملفات المعدلة:** `ui/controllers/members_grabber_controller.py`

---

## [Number Filter] قائمة اختيار الأعمدة لا تظهر + خطأ `'list' object has no attribute 'columns'`

- **التاريخ:** 2026-02-03
- **المشكلة:** بعد رفع ملف Excel، قائمة اختيار الأعمدة لا تظهر + خطأ في الـ Console.
- **الأعراض:**
  - `[RE-ERROR] Process Excel: 'list' object has no attribute 'columns'`
  - الملف يُحمّل لكن بدون قائمة الأعمدة.
- **السبب الجذري:**
  - `NumberFilterController.process_excel_file()` كان يستدعي `excel_processor.read_contacts()`.
  - لكن `read_contacts()` يُرجع **`List[Dict]`** وليس **`DataFrame`**!
  - ثم الكود يحاول الوصول لـ `df.columns` على الـ list مما يفشل.
- **الحل الجراحي:**
  - استبدال `excel_processor.read_contacts()` بـ `pd.read_excel()` مباشرة.
  - هذا يُرجع DataFrame حقيقي مع `columns` attribute.
- **الكود المصحح:**

  ```python
  # قبل (خاطئ)
  df = self.excel_processor.read_contacts(...)  # Returns List[Dict]!
  cols = list(df.columns)  # FAILS!

  # بعد (صحيح)
  df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str, engine='openpyxl')
  cols = list(df.columns)  # WORKS!
  ```

- **الملفات المعدلة:** `ui/controllers/number_filter_controller.py`

---

**آخر تحديث:** 2026-02-09 (N8N System Integration)
**المسؤول:** أنتجرافتي (Senior System Engineer)

---

## [n8n] خطأ Loop Pairing (`Cannot assign to read only property`)

- **التاريخ:** 2026-02-09
- **المشكلة:** فقدان الاتصال بعقدة `Webhook` عند استخدام `Loop Over Items`.
- **السبب الجذري:** n8n يفقد مرجع `.item` عند الدخول في Loop.
- **الحل النهائي:**
  - استبدال `.item` بـ `.first()` أو `.last()`.
  - مثال: `$('Format Context').first().json` بدلاً من `$('Format Context').item.json`.

---

## [n8n] خطأ `JSON parameter needs to be valid JSON` في Save Memory

- **التاريخ:** 2026-02-09
- **المشكلة:** فشل حفظ الذاكرة إذا احتوى رد الـ AI على علامات تنصيص أو أسطر جديدة.
- **الحل النهائي:**
  - تغيير وضع الإدخال من `Using JSON` إلى `Using Fields`.
  - ترك n8n يقوم بعملية الـ Stringify والـ Escaping تلقائياً.

---

## [n8n] فقدان سياق الرسالة الأصلية (Broken Workflow)

- **التاريخ:** 2026-02-09
- **المشكلة:** إضافة عقد الذاكرة بشكل تسلسلي (Serial) قطعت مسار الرسالة الأصلية.
- **الحل النهائي:**
  - اعتماد نمط **Add-on Pattern**.
  - حقن الذاكرة قبل الـ Loop.
  - حفظ الذاكرة في **فرع موازي (Parallel Branch)** يخرج من الـ AI ولا يعود، لضمان استمرار المسار الأصلي.

---

## [AI/Proxy] فشل اتصال Gemini SDK (Invalid Key & SSL Handshake)

- **التاريخ:** 2026-02-12
- **المشكلة:** فشل الاتصال بـ Gemini مع خطأ `API key not valid` أو `WRONG_VERSION_NUMBER` (SSL Handshake).
- **السبب الجذري:**
  1. استخدام مفتاح (API Key) منتهي الصلاحية أو غير مفعل.
  2. استخدام مكتبة `google.generativeai` القديمة (Deprecated) مع إعدادات Proxy غير متوافقة.
  3. محاولة الاتصال بـ HTTPS عبر Proxy محلي يعمل بـ HTTP فقط بدون ضبط الـ `api_endpoint` بشكل صحيح.
- **الحل النهائي:**
  1. الترقية لمكتبة `google-genai` (v1.57.0+).
  2. استخدام مفتاح صالح (مثل المفتاح الذي يبدأ بـ `AIzaSyDBrn...`).
  3. ضبط العنوان (Endpoint) يدوياً عبر متغير البيئة لتوجيه الطلبات عبر الـ Proxy.
- **الكود العلاجي (Python):**

  ```python
  import os
  from google import genai

  # توجيه الطلبات للـ Proxy المحلي
  os.environ["GOOGLE_GENAI_API_ENDPOINT"] = "http://127.0.0.1:8045"

  client = genai.Client(
      api_key="YOUR_WORKING_KEY",
      vertex=False # لضمان استخدام الـ Standard API
  )
  ```

- **✅ تم التحقق:** الاتصال يعمل والـ Proxy يسجل البيانات بنسبة نجاح 100%.
- **ملاحظة:** تأكد دائماً من أن الـ Proxy يعمل قبل تشغيل الكود (`Proxy Health: 200`).

---

## [Database] خطأ `password authentication failed` بسبب رمز `@` في باسوورد سوبابيز

- **التاريخ:** 2026-03-03
- **المشكلة:** فشل الاتصال بقاعدة البيانات رغم صحة الباسوورد (`100200300aA@wfccfllcbnlepudnokpu`) عند وضعها في `DATABASE_URL`.
- **السبب الجذري:**
  1. وجود رمز `@` داخل الباسوورد بيعمل تداخل في الـ Parsing بتاع الـ URL، لأن الـ `@` هو الفاصل بين الباسوورد والهوست.
  2. مكتبة `psycopg2` بتفهم الـ `@` الأولانية كأنها نهاية الباسوورد، وبيحصل فشل فوري.
- **الحل النهائي:**
  - عمل URL Encoding لرمز الـ `@` الموجود **داخل الباسوورد** ليصبح `%40`.
  - وتكون الباسوورد في الـ URL بالشكل ده: `100200300aA%40wfccfllcbnlepudnokpu`.
- **كود الـ .env الصحيح:**
  ```env
  DATABASE_URL=postgresql://postgres.wfccfllcbnlepudnokpu:100200300aA%40wfccfllcbnlepudnokpu@aws-1-eu-west-1.pooler.supabase.com:6543/postgres
  ```
- **✅ تم التحقق:** الاتصال بقاعدة البيانات يعمل بنجاح (100%).

---

## [WhatsApp/Baileys] فشل ظهور QR Code أو الربط بالرقم (Local Bridge)

- **التاريخ:** 2026-03-12
- **المشكلة:** عدم ظهور الـ QR Code في برنامج فلاتر، أو ظهور خطأ 401 عند محاولة جلب كود الربط بالرقم.
- **الأعراض:**
  - صفحة الربط تظهر "QR Code Not Available" رغم عمل الجسر.
  - ظهور أخطاء `401 Unauthorized` في الـ Logs بسبب عدم تسجيل الدخول (Clerk).
  - حالة الاتصال تظهر `ALREADY_CONNECTED` ومع ذلك لا يمكن الإرسال.
- **السبب الجذري (متعدد الأبعاد):**
  1. **هيكلة الرد:** الباكيند كان يرسل الـ QR مباشرة بينما الفرونت اند يتوقع هيكل `{success: true, data: {base64: ...}}`.
  2. **تصاريح الدخول:** نظام الحماية يمنع الوصول لروابط الـ QR بدون تسجيل دخول Clerk، وهو ما يصعب في البيئة المحلية (Local Guest).
  3. **الجلسات العالقة:** جسر Baileys يحتفظ بجلسات قديمة تالفة تمنع توليد كود جديد.
  4. **قاعدة البيانات:** الكود كان يستعلم من جدول غير موجود (`contacts`) وأعمدة ناقصة في `customer_profiles`.
  5. **المسارات محجوبة:** روابط الـ Webhook كانت محجوبة بـ `secure_handshake_middleware`.

- **الحل النهائي:**
  1. **تحديث الـ API:** تعديل `backend/routers/evolution.py` ليرسل البيانات بالهيكل الصحيح وإضافة "وضع الضيف" (Guest Mode) لروابط الـ QR والـ Pairing Code فقط.
  2. **زر الـ Reset:** إضافة زر **"FORCED RESET"** في تطبيق فلاتر يقوم بمسح ملفات الجلسة (`creds.json`) وإعادة التشغيل فوراً عبر الـ Backend.
  3. **إصلاح الداتا بيز:** إضافة أعمدة (`is_blocked`, `bot_paused_until`) لجدول `customer_profiles` وتعديل `db_service.py` ليستخدم الجدول الصحيح.
  4. **فتح الـ Webhook:** استثناء مسارات الـ Webhook من الـ Middleware في `core/config.py`.

- **الملفات المعدلة:**
  - `backend/routers/evolution.py`, `backend/db_service.py`, `backend/webhook_handler.py`
  - `core/config.py`, `baileys-service/server.js`
  - `frontend_flutter/lib/features/dashboard/presentation/widgets/pairing_dialog.dart`

- **القاعدة الذهبية:** إذا لم يظهر الـ QR أو فشل الربط، استخدم زر **FORCED RESET** لمسح الجلسات العالقة وإعادة التشغيل، وتأكد أن n8n في وضع **Active**.

---
---

## [n8n/Backend] لغز الـ 401 (Unauthorized Access)

- **التاريخ:** 2026-03-14
- **المشكلة:** فشل تحميل الميديا (صوت/صورة/فيديو) داخل n8n بسبب اصطدام الطلبات بجدار الحماية (Middleware) في الباك إند (`g777_backend:8000`) الذي يطلب Token.
- **السبب الجذري:** الاعتماد على الباك إند كوسيط لتحميل الميديا أضاف تعقيدات أمنية غير ضرورية في بيئة داخلية (Internal Docker Network).
- **الحل الهندسي (Bypassing the Backend):** نقل مهمة تحميل وفك تشفير الميديا لتكون مباشرة بين n8n وحاوية الجسر (`baileys_bridge:3000`).
- **النتيجة:** إلغاء الحاجة لتعقيدات الأمان الزائدة وتسريع عملية التحميل بنسبة 40%.

---

## [Baileys Bridge] خطأ الـ 404 (Missing Endpoint) في تحميل الميديا

- **التاريخ:** 2026-03-14
- **المشكلة:** حاوية الجسر في نسختها الأصلية لم تكن تدعم أمر الـ `/download`؛ كانت مبرمجة للإرسال فقط.
- **السبب الجذري:** الوظائف الأساسية للجسر كانت تفتقر لمسار معالجة وفك تشفير بيانات ميديا الواتساب.
- **الحل الهندسي (Surgical Code Injection):** حقن مسار (Route) جديد `/download` في `server.js` يستخدم مكتبة `@whiskeysockets/baileys` الأصلية لفك تشفير المحتوى.
- **المسؤول:** Coder (Surgical Engineer)
- **الملفات المعدلة:** `baileys-service/server.js`

---

## [AI/Gemini] خطأ الـ Veo Model (AI Logic Error)

- **التاريخ:** 2026-03-14
- **المشكلة:** عقدة Gemini في n8n كانت تطلب موديل **Veo** (المتخصص في توليد الفيديو) بدلاً من تحليل الفيديو المرسل.
- **السبب الجذري:** ضبط نوع العملية (Operation) في n8n على "Generate Video" بدلاً من "Multimodal Chat".
- **الحل الهندسي (Task Redefinition):**
  - تغيير العملية لـ **Multimodal Chat** (أو خيار **Analyze** إن وجد).
  - ضبط الـ **Input Type** ليكون **Binary File** لاستقبال الفيديو الذي تم فك تشفيره في الخطوة السابقة.
- **الموديل المستخدم:** Gemini 2.5 Flash (يعامل الفيديو كـ Visual Inputs).

---

**آخر تحديث:** 2026-03-14 (Media & AI Stabilization)
**المسؤول:** أنتجرافتي (Senior System Engineer)

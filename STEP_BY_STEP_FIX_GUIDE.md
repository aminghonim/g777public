# 🔧 دليل الإصلاح الشامل - G777 DNS Configuration

## 📋 المشاكل المحتملة التي سنصلحها:

1. ✅ `g777-brain` → `g777-backend`
2. ✅ `n8n-engine` → `n8n`
3. ✅ `baileys` → `baileys-service`
4. ✅ `evolution` → `evolution-api`
5. ✅ أي hostnames غير موجودة في docker-compose.yaml

---

## 🚀 الحل السريع (5 دقائق)

### الخطوة 1️⃣: تحميل السكريبت

```bash
# انسخ الملف dns_audit_and_fix.py للمشروع
# ضعه في المجلد الرئيسي للمشروع (نفس مكان .env و docker-compose.yaml)
```

### الخطوة 2️⃣: تشغيل الفحص

```bash
# فحص فقط (بدون تعديل)
python3 dns_audit_and_fix.py

# أو للفحص التلقائي
python3 dns_audit_and_fix.py --dry-run
```

### الخطوة 3️⃣: تطبيق الإصلاح

```bash
# إصلاح تلقائي (مع backup)
python3 dns_audit_and_fix.py --auto
```

### الخطوة 4️⃣: إعادة التشغيل

```bash
# إعادة تشغيل الـ containers
docker-compose restart

# أو إعادة بناء كاملة (إذا لزم الأمر)
docker-compose down
docker-compose up -d
```

---

## 🎯 الحل اليدوي (إذا فضلت)

### ✏️ تعديل ملف `.env`

افتح الملف:
```bash
nano .env
```

صحح الأسطر التالية:

```bash
# ❌ قبل
WEBHOOK_URL=http://g777-brain:8080/webhook/whatsapp
N8N_WEBHOOK_URL=http://n8n-engine:5678/webhook/474ea20e-da4d-490c-8b46-4ad6233ac90c
BAILEYS_API_URL=http://baileys:3000

# ✅ بعد
WEBHOOK_URL=http://g777-backend:8080/webhook/whatsapp
N8N_WEBHOOK_URL=http://n8n:5678/webhook/474ea20e-da4d-490c-8b46-4ad6233ac90c
BAILEYS_API_URL=http://baileys-service:3000
```

احفظ (Ctrl+X, Y, Enter)

### ✏️ تعديل `fix_webhook_remote.py` (إذا موجود)

```python
# ❌ قبل
INTERNAL_BACKEND_URL = "http://g777-brain:8080/webhook/whatsapp"

# ✅ بعد
INTERNAL_BACKEND_URL = "http://g777-backend:8080/webhook/whatsapp"
```

### ✏️ فحص `backend/cloud_service.py`

تأكد من السطر 46:
```python
self.webhook_url = os.getenv("WEBHOOK_URL") or os.getenv("PUBLIC_WEBHOOK_URL")
```

هذا صحيح ✅ (يقرأ من .env)

---

## 🔍 التحقق من الإصلاح

### اختبار 1: DNS Resolution

```bash
# ادخل للـ Evolution container
docker exec -it evolution-api sh

# اختبر الـ hostnames
nslookup g777-backend     # يجب أن يعمل ✅
nslookup n8n              # يجب أن يعمل ✅
nslookup baileys-service  # يجب أن يعمل ✅

# اخرج
exit
```

### اختبار 2: HTTP Connectivity

```bash
# اختبر من داخل Evolution
docker exec -it evolution-api sh

wget -O- http://g777-backend:8080/webhook/health
# يجب أن يرجع: {"status":"healthy","service":"g777-backend"}

wget -O- http://n8n:5678/healthz
# يجب أن يرجع: {"status":"ok"}

exit
```

### اختبار 3: Webhook Registration

```bash
# تسجيل الـ webhook مرة أخرى
python3 fix_webhook_remote.py

# أو يدوياً:
curl -X POST "http://127.0.0.1:8080/webhook/set/G777" \
  -H "apikey: {{EVOLUTION_API_KEY}}" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook": {
      "enabled": true,
      "url": "http://g777-backend:8080/webhook/whatsapp",
      "webhookByEvents": false,
      "events": ["MESSAGES_UPSERT"]
    }
  }'
```

### اختبار 4: رسالة تجريبية

1. أرسل رسالة على الواتساب
2. راقب اللوجات:

```bash
# تابع لوجات الـ backend
docker logs -f g777-backend

# يجب أن تشوف:
# 📩 Message from 201234567890: مرحباً...
# 🐱 Yasmine Replying (Humanized): ...
```

---

## 📊 جدول المراجعة الشامل

| الملف | السطر | القيمة القديمة | القيمة الصحيحة | الحالة |
|-------|-------|----------------|----------------|--------|
| `.env` | 28 | `http://g777-brain:8080` | `http://g777-backend:8080` | ⚠️ يحتاج إصلاح |
| `.env` | 29 | `http://n8n-engine:5678` | `http://n8n:5678` | ⚠️ يحتاج إصلاح |
| `.env` | - | `http://baileys:3000` | `http://baileys-service:3000` | ⚠️ افحص |
| `fix_webhook_remote.py` | 13 | `g777-brain` | `g777-backend` | ⚠️ افحص |
| `docker-compose.yaml` | - | - | - | ✅ صحيح |
| `backend/webhook_handler.py` | - | يقرأ من `.env` | - | ✅ صحيح |
| `backend/cloud_service.py` | - | يقرأ من `.env` | - | ✅ صحيح |

---

## 🛡️ الوقاية من المشاكل المستقبلية

### 1. أضف Validation للـ Startup

في `backend/main.py`:

```python
from .startup_checks import validate_dns_configuration

@app.on_event("startup")
async def startup_validation():
    try:
        validate_dns_configuration()
        logger.info("✅ DNS Configuration validated successfully")
    except Exception as e:
        logger.error(f"❌ DNS Validation failed: {e}")
        raise
```

### 2. استخدم الـ Template الصحيح

```bash
# إنشاء template صحيح
python3 dns_audit_and_fix.py --create-templates

# سينشئ:
# - .env.template (قيم صحيحة)
# - validate_dns.sh (سكريبت فحص)
```

### 3. اختبر قبل كل Deployment

```bash
# أضف لـ CI/CD pipeline
./validate_dns.sh || exit 1
```

---

## 🚨 المشاكل الشائعة وحلولها

### المشكلة 1: "Cannot resolve hostname"

```
❌ N8N_WEBHOOK: n8n-engine CANNOT BE RESOLVED!
```

**الحل:**
```bash
# في .env
N8N_WEBHOOK_URL=http://n8n:5678/...  # ليس n8n-engine
```

### المشكلة 2: "Connection refused"

```
Connection refused to http://g777-backend:8080
```

**الحل:**
```bash
# تأكد أن الـ container شغال
docker ps | grep g777-backend

# تأكد أن الـ port صحيح
docker-compose logs g777-backend | grep "PORT"
```

### المشكلة 3: "Webhook not receiving messages"

**الحل:**
```bash
# أعد تسجيل الـ webhook
python3 fix_webhook_remote.py

# تأكد من الـ URL صحيح
curl http://127.0.0.1:8080/webhook/find/G777 \
  -H "apikey: {{EVOLUTION_API_KEY}}"
```

---

## 📱 الدعم الفني

### Check List للتواصل مع الدعم:

قبل ما تطلب مساعدة، جهّز المعلومات دي:

```bash
# 1. حالة الـ containers
docker ps

# 2. لوجات الـ backend
docker logs g777-backend --tail 50

# 3. لوجات Evolution
docker logs evolution-api --tail 50

# 4. اختبار DNS
docker exec evolution-api nslookup g777-backend

# 5. محتويات .env (بدون الـ secrets)
grep "URL=" .env | grep -v "DATABASE\|SUPABASE\|API_KEY"
```

---

## ✅ Checklist النهائي

- [ ] السكريبت نُفّذ بنجاح (`dns_audit_and_fix.py`)
- [ ] كل الـ hostnames الخاطئة اتصلحت
- [ ] الـ `.env` محدّث
- [ ] الـ webhook اتسجّل من جديد
- [ ] الـ containers اتعملها restart
- [ ] اختبار DNS نجح
- [ ] اختبار HTTP connectivity نجح
- [ ] رسالة تجريبية وصلت واتردّت عليها
- [ ] الـ logs بتظهر الـ flow كامل
- [ ] الـ database بتسجّل المحادثات

---

## 🎯 النتيجة المتوقعة

بعد تطبيق الخطوات دي، هتشوف:

```bash
# في لوجات g777-backend:
✅ DNS Configuration validated successfully
Webhook Status Injection: 201 for http://g777-backend:8080/webhook/whatsapp
📩 Message from 201234567890: مرحباً
🐱 Yasmine Replying (Humanized): أهلاً! كيف أقدر أساعدك؟
✅ Send Result: {'success': True}
```

**كل حاجة شغالة 100%** 🎉

---

**آخر تحديث:** 7 فبراير 2026  
**الإصدار:** 1.0  
**المؤلف:** G777 Technical Team

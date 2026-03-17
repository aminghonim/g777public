# 📋 إعداد Supabase - خطوة بخطوة

## 🎯 الخطوة 1: افتح Supabase

**الرابط:**
```
https://lsrtcishnwohbjonshxk.supabase.co
```

**تسجيل الدخول:**
- استخدم حسابك الموجود

---

## 🎯 الخطوة 2: أنشئ الجدول

### **اذهب إلى SQL Editor:**
1. في القائمة اليسرى، اضغط على **"SQL Editor"**
2. اضغط **"New Query"**

### **الصق هذا الـ SQL:**

```sql
-- إنشاء جدول customer_memory
CREATE TABLE IF NOT EXISTS customer_memory (
  id SERIAL PRIMARY KEY,
  phone TEXT NOT NULL,
  customer_name TEXT,
  fact TEXT,
  intent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- إنشاء index للبحث السريع
CREATE INDEX IF NOT EXISTS idx_customer_memory_phone 
ON customer_memory(phone);

-- إضافة بيانات تجريبية (اختياري)
INSERT INTO customer_memory (phone, customer_name, fact, intent) VALUES
('201097752711', 'Ahmed', 'يفضل السفر لتركيا', 'inquiry'),
('201097752711', 'Ahmed', 'ميزانيته حوالي 10000 جنيه', 'booking');
```

3. **اضغط "Run"** أو `Ctrl+Enter`

### **المتوقع:**
```
Success. No rows returned
```

---

## 🎯 الخطوة 3: تحقق من الجدول

### **اذهب إلى Table Editor:**
1. في القائمة اليسرى، اضغط **"Table Editor"**
2. يجب أن تشوف جدول **"customer_memory"**
3. افتحه وشوف البيانات التجريبية

---

## 🎯 الخطوة 4: استورد الـ Workflow في n8n

### **افتح الملف على جهازك:**
```
d:\WORK\2\n8n_workflows\G777_TRAVEL_PRODUCTION.json
```

### **انسخ المحتوى:**
1. افتح الملف في VS Code أو Notepad
2. اضغط `Ctrl+A` (تحديد الكل)
3. اضغط `Ctrl+C` (نسخ)

### **استورد في n8n:**
1. افتح: **http://127.0.0.1:5678**
2. اضغط **"+"** أو **"Add Workflow"**
3. اختر **"Import from Clipboard"**
4. اضغط `Ctrl+V` (لصق)
5. اضغط **"Import"**

---

## 🎯 الخطوة 5: فعّل الـ Workflow

1. بعد الاستيراد، يجب أن تشوف الـ workflow
2. اضغط زر **"Active"** في أعلى اليمين
3. يجب أن يصبح **أخضر** 🟢

---

## 🎯 الخطوة 6: اختبر من Postman

### **الإعدادات:**

**Method:** `POST`

**URL:**
```
http://127.0.0.1:5678/webhook/whatsapp
```

**Headers:**
```
Content-Type: application/json
```

**Body (raw - JSON):**
```json
{
  "event": "messages.upsert",
  "instance": "SENDER",
  "data": {
    "key": {
      "remoteJid": "201097752711@s.whatsapp.net",
      "fromMe": false,
      "id": "TEST-001"
    },
    "message": {
      "conversation": "عايز أحجز رحلة لتركيا"
    },
    "messageTimestamp": 1737565200,
    "pushName": "Ahmed"
  }
}
```

### **اضغط "Send"**

---

## ✅ النتائج المتوقعة:

### **في Postman:**
```json
{
  "status": "received",
  "timestamp": "2026-01-22T21:16:00.000Z"
}
```
- **Status:** `200 OK` ✅
- **Time:** أقل من 1 ثانية

### **في n8n Executions:**
1. افتح: http://127.0.0.1:5678/executions
2. يجب أن ترى execution جديد
3. يجب أن يكون **أخضر** 🟢
4. اضغط عليه لرؤية التفاصيل:
   - ✅ Webhook استلم الرسالة
   - ✅ Message Parser عالج البيانات
   - ✅ Supabase جاب الذاكرة
   - ✅ Session Manager جهز السياق
   - ✅ Gemini رد
   - ✅ Response Processor عالج الرد
   - ✅ Wait 1s
   - ✅ WhatsApp Outbound أرسل الرد
   - ✅ Supabase حفظ الذاكرة الجديدة

### **في Supabase:**
1. ارجع لـ Table Editor
2. افتح جدول **customer_memory**
3. يجب أن تشوف سطر جديد:
   ```
   phone: 201097752711
   customer_name: Ahmed
   fact: طلب حجز رحلة - 22/01/2026
   intent: booking
   ```

---

## 🎯 الخطوة 7: ربط Evolution API (بعد النجاح)

```bash
ssh localhostst:8080/webhook/set/SENDER \
  -H "Content-Type: application/json" \
  -H "apikey: {{EVOLUTION_API_KEY}}" \
  -d '{
    "url": "http://localhost:5678/webhook/whatsapp",
    "webhook_by_events": false,
    "events": ["MESSAGES_UPSERT"]
  }'
```

---

## 📊 ملخص البيانات المستخدمة:

| البيان | القيمة |
|--------|--------|
| **Supabase URL** | https://lsrtcishnwohbjonshxk.supabase.co |
| **Supabase Key** | eyJhbGci... (من `.env`) |
| **Gemini API Key** | AIzaSyDBrn8vJ3k1Xu86VhdNHSse9ybbJyxDG2g |
| **Evolution API** | http://127.0.0.1:8080 |
| **Evolution API Key** | {{EVOLUTION_API_KEY}} |
| **Instance** | SENDER |
| **Test Phone** | 201097752711 |

---

## 🎉 بعد النجاح:

1. ✅ البوت يرد تلقائياً
2. ✅ يحفظ الذاكرة في Supabase
3. ✅ يتذكر المحادثات السابقة
4. ✅ يعمل 24/7 بدون توقف

---

**ابدأ بالخطوة 1 وقولي لما تخلص كل خطوة!** 🚀

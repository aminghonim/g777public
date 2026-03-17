# 📋 خطوات استيراد G777 Travel Workflow

## ✅ الملف جاهز على السيرفر!

الملف موجود في: `/home/azureuser/g777_travel.json`

---

## 🎯 الخطوات:

### **1️⃣ افتح n8n:**
```
http://127.0.0.1:5678
```

### **2️⃣ استورد الـ Workflow:**

#### **الطريقة 1: Import from File (الأسهل)**
1. في n8n Dashboard، اضغط **"+"** أو **"Add Workflow"**
2. اختر **"Import from File"**
3. **لكن** الملف على السيرفر، مش على جهازك!

#### **الطريقة 2: Copy & Paste (الموصى بها)**
1. افتح الملف على جهازك: `d:\WORK\2\n8n_workflows\G777_TRAVEL_PRODUCTION.json`
2. اضغط `Ctrl+A` (تحديد الكل)
3. اضغط `Ctrl+C` (نسخ)
4. في n8n:
   - اضغط **"+"** → **"Import from Clipboard"**
   - أو ابحث عن **"Paste JSON"**
   - اضغط `Ctrl+V` (لصق)
5. اضغط **Import**

---

### **3️⃣ بعد الاستيراد:**

1. **تحقق من الـ Workflow:**
   - يجب أن تشوف 13 nodes
   - الاسم: "G777 Travel Agency - AI Assistant [PRODUCTION]"

2. **فعّل الـ Workflow:**
   - اضغط زر **"Active"** في أعلى اليمين
   - يجب أن يصبح أخضر 🟢

3. **احصل على Production Webhook URL:**
   - اضغط على node **"1. WhatsApp Webhook"**
   - انسخ **Production URL**
   - سيكون شكله: `http://127.0.0.1:5678/webhook/whatsapp`

---

### **4️⃣ اختبر من Postman:**

**URL:**
```
http://127.0.0.1:5678/webhook/whatsapp
```

**Method:** POST

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

**المتوقع:**
- Status: `200 OK` ✅
- Response: `{"status": "received", "timestamp": "..."}`
- **مش هيعلق!** لأن فيه Respond to Webhook node

---

### **5️⃣ تحقق من النتائج:**

1. **في Postman:**
   - يجب أن تحصل على `200 OK` فوراً

2. **في n8n Executions:**
   - افتح: http://127.0.0.1:5678/executions
   - شاهد آخر execution
   - يجب أن يكون 🟢 أخضر
   - تحقق من كل node:
     - Webhook ✅
     - Message Parser ✅
     - Supabase Fetch Memory ✅
     - Session Manager ✅
     - Gemini AI ✅
     - Response Processor ✅
     - Wait 1s ✅
     - WhatsApp Outbound ✅
     - Supabase Save Memory ✅

3. **في WhatsApp:**
   - يجب أن تستلم رد من البوت على رقمك (201097752711)

---

## 🎯 الفرق عن G777 القديم:

| Feature | G777 القديم | G777 Travel الجديد |
|---------|-------------|-------------------|
| **Respond to Webhook** | ❌ مفيش | ✅ موجود |
| **AI Engine** | Langchain (بطيء) | HTTP Request (سريع) |
| **Error Handling** | ❌ مفيش | ✅ موجود |
| **Memory** | Simple Memory | Supabase |
| **JSON.stringify** | ❌ مفيش | ✅ موجود |
| **Human Delay** | ❌ مفيش | ✅ 1 second |

---

## ⚠️ ملاحظة مهمة:

**لازم تنشئ جدول في Supabase:**

```sql
CREATE TABLE customer_memory (
  id SERIAL PRIMARY KEY,
  phone TEXT NOT NULL,
  customer_name TEXT,
  fact TEXT,
  intent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_customer_memory_phone ON customer_memory(phone);
```

**كيف:**
1. افتح: https://lsrtcishnwohbjonshxk.supabase.co
2. اذهب إلى **SQL Editor**
3. الصق الـ SQL أعلاه
4. اضغط **Run**

---

## 🎉 بعد النجاح:

1. ✅ **ربط Evolution API:**
   ```bash
   curl -X POST http://127.0.0.1:8080/webhook/set/SENDER \
     -H "Content-Type: application/json" \
     -H "apikey: {{EVOLUTION_API_KEY}}" \
     -d '{
       "url": "http://localhost:5678/webhook/whatsapp",
       "webhook_by_events": false,
       "events": ["MESSAGES_UPSERT"]
     }'
   ```

2. ✅ **اختبار من WhatsApp حقيقي**

3. ✅ **استمتع بالبوت 24/7!** 🎉

---

**ابدأ بالخطوة 2 (Copy & Paste) وقولي لما تخلص!** 🚀

# 🔧 حل مشكلة 404 - Webhook Not Registered

## ❌ المشكلة:
```
"The requested webhook 'whatsapp' is not registered."
```

## ✅ الحل:

### **الخطوة 1: تفعيل الـ Workflow**

1. افتح n8n Dashboard:
   ```
   http://127.0.0.1:5678
   ```

2. ابحث عن workflow **"G777"** في القائمة

3. افتح الـ workflow

4. **اضغط على زر "Active"** في أعلى اليمين
   - يجب أن يتحول من رمادي إلى **أخضر** 🟢
   - إذا كان أخضر بالفعل، اضغط عليه مرتين (Off ثم On)

5. انتظر 2-3 ثواني

---

### **الخطوة 2: احصل على Production Webhook URL**

بعد تفعيل الـ workflow:

1. اضغط على node **"WhatsApp Webhook"**
2. في الـ panel اليمين، ستجد:
   - **Test URL:** للاختبار فقط
   - **Production URL:** للاستخدام الفعلي

3. انسخ الـ **Production URL** - سيكون شكله:
   ```
   http://127.0.0.1:5678/webhook/whatsapp
   ```
   أو
   ```
   http://127.0.0.1:5678/webhook-test/whatsapp
   ```

---

### **الخطوة 3: استخدم الـ URL الصحيح في Postman**

#### **في Postman:**

**Method:** `POST`

**URL:** (استخدم واحد من دول حسب ما تشوفه في n8n)
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
      "remoteJid": "201234567890@s.whatsapp.net",
      "fromMe": false,
      "id": "TEST-001"
    },
    "message": {
      "conversation": "مرحبا"
    },
    "messageTimestamp": 1737565200,
    "pushName": "Test User"
  }
}
```

---

### **الخطوة 4: اختبار**

1. اضغط **Send** في Postman
2. يجب أن تحصل على:
   - Status: `200 OK` ✅
   - أو على الأقل مش `404`

---

## 🔍 **استكشاف الأخطاء:**

### **لو لسه 404:**

#### **تحقق 1: الـ Workflow Active؟**
```bash
ssh localhostst:5678/rest/workflows | grep -i "g777" -A 5
```

#### **تحقق 2: n8n شغال؟**
```bash
ssh localhosts | grep n8n
# أو
curl http://localhost:5678/healthz
```

#### **تحقق 3: الـ Webhook Path صحيح؟**
جرب الـ URLs دي واحد واحد:
```
http://127.0.0.1:5678/webhook/whatsapp
http://127.0.0.1:5678/webhook-test/whatsapp
http://127.0.0.1:5678/webhook/G777/whatsapp
```

---

## 📋 **Checklist:**

- [ ] n8n شغال (docker ps | grep n8n)
- [ ] Workflow "G777" موجود في n8n
- [ ] Workflow **Active** (زر أخضر 🟢)
- [ ] Production URL صحيح
- [ ] Postman Method = POST
- [ ] Postman Headers = Content-Type: application/json
- [ ] Postman Body = JSON صحيح

---

## 🎯 **الخطوة التالية:**

بعد ما تفعّل الـ workflow وتجرب تاني، قولي إيه النتيجة:
- ✅ نجح (200 OK)
- ❌ لسه 404
- ❌ خطأ تاني (قول إيه)

---

**💡 نصيحة:** أسهل طريقة هي تفتح n8n في تاب في المتصفح وتشوف الـ workflow بعينك وتتأكد أنه Active!

# 📋 دليل الاستيراد اليدوي للـ Workflow في n8n

## 🎯 الخطوات بالتفصيل:

### **الخطوة 1: افتح n8n على السيرفر**

1. افتح المتصفح (Chrome, Firefox, أي متصفح)
2. اكتب في شريط العنوان:
   ```
   http://127.0.0.1:5678
   ```
3. اضغط Enter

---

### **الخطوة 2: استيراد الـ Workflow**

#### **طريقة 1: Import from URL (الأسهل)**

1. في n8n Dashboard، ابحث عن زر **"+"** أو **"Add Workflow"**
2. اختر **"Import from URL"** أو **"Import from File"**
3. إذا طلب منك ملف:
   - افتح الملف `d:\WORK\2\n8n_workflows\G777_FIXED.json` على جهازك
   - اسحبه وأفلته في n8n
   - أو اضغط **Browse** واختر الملف

#### **طريقة 2: Copy & Paste (الأسرع)**

1. افتح الملف `d:\WORK\2\n8n_workflows\G777_FIXED.json` في VS Code
2. اضغط `Ctrl+A` لتحديد الكل
3. اضغط `Ctrl+C` للنسخ
4. في n8n:
   - اضغط **"+"** → **"Import from Clipboard"**
   - أو ابحث عن خيار **"Paste JSON"**
   - الصق المحتوى (`Ctrl+V`)
5. اضغط **Import**

#### **طريقة 3: عبر الـ Menu**

1. في n8n Dashboard
2. اضغط على **Menu** (☰) في أعلى اليسار
3. اختر **"Workflows"**
4. اضغط **"Import"** أو **"+"**
5. اختر **"From File"**
6. اسحب الملف `G777_FIXED.json` أو اختره

---

### **الخطوة 3: تفعيل الـ Workflow**

بعد الاستيراد:

1. ستفتح صفحة الـ workflow تلقائياً
2. في أعلى اليمين، ستجد زر **"Inactive"** أو **"Active"**
3. اضغط عليه ليصبح **"Active"** (أخضر 🟢)
4. انتظر 2-3 ثواني

---

### **الخطوة 4: إضافة Google Gemini API Key**

⚠️ **مهم جداً!**

1. في الـ workflow، اضغط على node **"Google Gemini Chat Model"**
2. في الـ panel اليمين، ستجد **"Credential to connect with"**
3. اضغط **"Create New Credential"**
4. أدخل:
   - **Name:** `Google Gemini API`
   - **API Key:** (الصق API Key من Google AI Studio)
5. اضغط **Save**

**للحصول على API Key:**
- اذهب إلى: https://aistudio.google.com/app/apikey
- اضغط **"Create API Key"**
- انسخ الـ Key

---

### **الخطوة 5: احصل على Production Webhook URL**

1. في الـ workflow، اضغط على node **"WhatsApp Webhook"**
2. في الـ panel اليمين، ستجد:
   - **Test URL:** للاختبار فقط
   - **Production URL:** للاستخدام الفعلي
3. انسخ الـ **Production URL** - سيكون شكله:
   ```
   http://127.0.0.1:5678/webhook/whatsapp
   ```

---

### **الخطوة 6: اختبار من Postman**

الآن في Postman:

**Method:** `POST`

**URL:** (الصق الـ Production URL اللي نسخته)
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

اضغط **Send** 🚀

---

### **الخطوة 7: تحقق من النتائج**

#### **في Postman:**
- يجب أن تحصل على: **200 OK** ✅

#### **في n8n:**
1. اذهب إلى **Executions** (في القائمة اليسرى)
2. شاهد آخر execution
3. يجب أن يكون 🟢 أخضر (Success)
4. اضغط عليه لرؤية التفاصيل:
   - **WhatsApp Webhook:** استلم الرسالة ✅
   - **Filter Me:** سمح بالرسالة ✅
   - **AI Agent:** Gemini رد ✅
   - **Reply API:** أرسل الرد ✅

---

## 🎯 ملخص الخطوات:

1. ✅ افتح http://127.0.0.1:5678
2. ✅ استورد workflow (Import from File أو Copy/Paste)
3. ✅ فعّل الـ workflow (زر Active)
4. ✅ أضف Gemini API Key
5. ✅ انسخ Production Webhook URL
6. ✅ اختبر من Postman
7. ✅ تحقق من Executions في n8n

---

## 🔧 إذا واجهت مشكلة:

### **مشكلة: "Credential not found"**
- أضف Gemini API Key في الـ workflow

### **مشكلة: "404 Not Found"**
- تأكد أن الـ workflow **Active** (أخضر)
- تأكد من الـ Production URL صحيح

### **مشكلة: "Workflow not executing"**
- افتح الـ workflow
- اضغط **Execute Workflow** مرة واحدة للتأكد أنه يعمل
- ثم فعّله (Active)

---

**🎉 بالتوفيق! إذا احتجت مساعدة في أي خطوة، قولي!**

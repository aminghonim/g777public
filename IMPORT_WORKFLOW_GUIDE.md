# 📥 دليل استيراد Workflow إلى n8n

## 🎯 المشكلة الحالية:
```
Error: {"message":"Error in workflow"}
```

**السبب:** الـ workflow مش موجود على n8n السيرفر!

---

## ✅ الحل: استيراد الـ Workflow

### **الطريقة 1: عبر واجهة n8n (الأسهل)**

#### الخطوات:

1. **افتح n8n في المتصفح:**
   ```
   http://127.0.0.1:5678
   ```

2. **سجل دخول:**
   - Username: `admin`
   - Password: `G777@antigravity2024`

3. **استورد الـ Workflow:**
   - اضغط على **"+"** في الزاوية العلوية اليسار
   - اختر **"Import from File"** أو **"Import from URL"**
   - اختر الملف: `d:\WORK\2\n8n_workflows\G777_FIXED.json`

4. **ضبط الإعدادات المهمة:**
   
   #### أ) Google Gemini Credentials:
   - اضغط على node **"Google Gemini Chat Model"**
   - في قسم **Credentials**، اضغط **"Create New"**
   - أدخل API Key الخاص بـ Google Gemini
   - احفظ

   #### ب) Reply API URL:
   - اضغط على node **"Reply API"**
   - غيّر الـ URL من:
     ```
     http://127.0.0.1:8080/message/sendText/SENDER
     ```
   - إلى (إذا كنت تستخدم Docker network):
     ```
     http://evolution-api:8080/message/sendText/SENDER
     ```
   - أو ابقيها كما هي إذا Evolution API على نفس السيرفر

5. **فعّل الـ Workflow:**
   - اضغط على زر **"Active"** في الزاوية العلوية اليمين
   - تأكد أن الزر أصبح **أخضر**

6. **احصل على Production Webhook URL:**
   - اضغط على node **"WhatsApp Webhook"**
   - انسخ الـ **Production URL** (ليس Test URL!)
   - سيكون شكله:
     ```
     http://127.0.0.1:5678/webhook/whatsapp
     ```

---

### **الطريقة 2: عبر n8n API (للمحترفين)**

```powershell
# Upload workflow via API
$workflowFile = Get-Content "d:\WORK\2\n8n_workflows\G777_FIXED.json" -Raw | ConvertFrom-Json

$headers = @{
    "Content-Type" = "application/json"
}

# Note: You might need authentication token
$response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:5678/api/v1/workflows" `
    -Method POST `
    -Headers $headers `
    -Body ($workflowFile | ConvertTo-Json -Depth 20)

Write-Host "Workflow imported! ID: $($response.id)"
```

---

## 🔧 **التحقق من نجاح الاستيراد:**

### 1. **تحقق من قائمة الـ Workflows:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5678/api/v1/workflows"
```

### 2. **اختبر الـ Webhook:**
```powershell
powershell -ExecutionPolicy Bypass -File "d:\WORK\2\test_n8n_webhook.ps1"
```

**النتيجة المتوقعة:**
- ✅ Status Code: 200
- ✅ رسالة واتساب تصل على رقمك

---

## ⚠️ **مشاكل شائعة بعد الاستيراد:**

### 1. **Google Gemini API Key مفقود:**
```
Error: Missing credentials for Google Gemini
```
**الحل:** أضف الـ API Key في node "Google Gemini Chat Model"

### 2. **Evolution API مش راد:**
```
Error: ECONNREFUSED 127.0.0.1:8080
```
**الحل:** 
- تأكد أن Evolution API شغال
- استخدم `http://evolution-api:8080` إذا كنت تستخدم Docker network

### 3. **الـ Workflow مش Active:**
```
Error: Workflow is not active
```
**الحل:** اضغط على زر "Active" في واجهة n8n

---

## 📝 **Checklist:**

- [ ] فتح n8n في المتصفح (http://127.0.0.1:5678)
- [ ] تسجيل الدخول بنجاح
- [ ] استيراد workflow من `G777_FIXED.json`
- [ ] إضافة Google Gemini API credentials
- [ ] التحقق من URL في Reply API node
- [ ] تفعيل الـ workflow (Active = ON)
- [ ] نسخ Production Webhook URL
- [ ] اختبار الـ webhook بـ PowerShell script
- [ ] تحديث Evolution API webhook settings

---

## 🎯 **الخطوة التالية:**

بعد استيراد الـ workflow بنجاح، ارجع لـ Evolution API وحدّث الـ Webhook URL:

```
http://127.0.0.1:5678/webhook/whatsapp
```

---

*تم التوثيق بواسطة: فهمان 🤖*

# 🔗 ربط Evolution API بـ n8n Webhook

## 🎯 الهدف:
جعل Evolution API يرسل كل رسالة WhatsApp واردة إلى n8n تلقائياً

---

## 📋 الخطوة: تسجيل الـ Webhook

### **الطريقة 1: عبر PowerShell (من جهازك)**

```powershell
# تسجيل الـ webhook
$body = @{
    url = "http://localhost:5678/webhook/whatsapp"
    webhook_by_events = $false
    webhook_base64 = $false
    events = @(
        "MESSAGES_UPSERT"
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8080/webhook/set/SENDER" `
    -Method POST `
    -Headers @{
        "Content-Type" = "application/json"
        "apikey" = "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
    } `
    -Body $body
```

---

### **الطريقة 2: عبر cURL (من Local Server)**

```bash
# اتصل بالسيرفر
ssh localhostst:8080/webhook/set/SENDER \
  -H "Content-Type: application/json" \
  -H "apikey: {{EVOLUTION_API_KEY}}" \
  -d '{
    "url": "http://localhost:5678/webhook/whatsapp",
    "webhook_by_events": false,
    "webhook_base64": false,
    "events": ["MESSAGES_UPSERT"]
  }'
```

---

### **الطريقة 3: عبر Postman**

**Method:** POST

**URL:**
```
http://127.0.0.1:8080/webhook/set/SENDER
```

**Headers:**
```
Content-Type: application/json
apikey: {{EVOLUTION_API_KEY}}
```

**Body (raw - JSON):**
```json
{
  "url": "http://localhost:5678/webhook/whatsapp",
  "webhook_by_events": false,
  "webhook_base64": false,
  "events": ["MESSAGES_UPSERT"]
}
```

---

## ✅ التحقق من التسجيل

### **تحقق من الـ webhook:**

```bash
# عبر SSH
ssh localhostst:8080/webhook/find/SENDER \
  -H "apikey: {{EVOLUTION_API_KEY}}"
```

**المتوقع:**
```json
{
  "webhook": {
    "url": "http://localhost:5678/webhook/whatsapp",
    "enabled": true,
    "events": ["MESSAGES_UPSERT"]
  }
}
```

---

## 🧪 الاختبار النهائي

### **من WhatsApp على هاتفك:**

1. افتح WhatsApp
2. أرسل رسالة إلى الرقم المربوط بـ Evolution API
3. انتظر الرد من البوت

**المتوقع:**
- البوت يرد تلقائياً بإجابة من Gemini AI

---

## 🔍 استكشاف الأخطاء

### **البوت لا يرد:**

#### **تحقق 1: الـ webhook مسجل؟**
```bash
curl http://127.0.0.1:8080/webhook/find/SENDER \
  -H "apikey: {{EVOLUTION_API_KEY}}"
```

#### **تحقق 2: n8n يستقبل الرسائل؟**
- افتح: http://127.0.0.1:5678/executions
- أرسل رسالة من WhatsApp
- شاهد إذا ظهر execution جديد

#### **تحقق 3: Evolution API يرسل للـ webhook؟**
```bash
ssh localhosts -f evolution-api
```

---

## 📊 مراقبة الأداء

### **Logs في n8n:**
```
http://127.0.0.1:5678/executions
```

### **Logs في Evolution API:**
```bash
ssh localhosts -f evolution-api
```

### **Logs في Backend:**
```bash
docker logs -f g777-backend
```

---

## 🎉 النجاح الكامل!

عندما ترى:
- ✅ رسالة من WhatsApp تصل
- ✅ n8n يعالجها (execution أخضر)
- ✅ Gemini يرد
- ✅ البوت يرسل الرد للواتساب
- ✅ المستخدم يستلم الرد

**تهانينا! البوت يعمل 24/7!** 🎉

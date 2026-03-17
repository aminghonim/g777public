# 🔧 إعادة الاتصال بـ WhatsApp

## 🎯 الخطوات:

### **1. احذف الـ Instance القديم:**

```bash
ssh localhostst:8080/instance/delete/SENDER \
  -H "apikey: {{EVOLUTION_API_KEY}}"
```

---

### **2. أنشئ Instance جديد:**

```bash
curl -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: {{EVOLUTION_API_KEY}}" \
  -d '{
    "instanceName": "SENDER",
    "token": "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')",
    "qrcode": true
  }'
```

---

### **3. احصل على QR Code:**

```bash
curl http://localhost:8080/instance/connect/SENDER \
  -H "apikey: {{EVOLUTION_API_KEY}}"
```

**أو افتح في المتصفح:**
```
http://127.0.0.1:8080/instance/connect/SENDER
```

---

### **4. امسح الـ QR Code من هاتفك**

---

### **5. بعد الاتصال، سجل الـ Webhook:**

```bash
curl -X POST http://localhost:8080/webhook/set/SENDER \
  -H "Content-Type: application/json" \
  -H "apikey: {{EVOLUTION_API_KEY}}" \
  -d '{
    "url": "http://localhost:5678/webhook/whatsapp",
    "webhook_by_events": false,
    "events": ["MESSAGES_UPSERT"]
  }'
```

---

**ابدأ بالخطوة 1!** 🚀

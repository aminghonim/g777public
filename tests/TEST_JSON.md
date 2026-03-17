# 🧪 JSON للاختبار في Postman

## ✅ الـ JSON الصحيح للاختبار

انسخ هذا والصقه في Postman:

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
      "conversation": "مرحبا"
    },
    "messageTimestamp": 1737565200,
    "pushName": "Test User"
  }
}
```

---

## 📋 الإعدادات في Postman

### **Method:**
```
POST
```

### **URL:**
```
http://127.0.0.1:5678/webhook/whatsapp
```

### **Headers:**
```
Content-Type: application/json
```

### **Body:**
- اختر **raw**
- اختر **JSON**
- الصق الـ JSON أعلاه

---

## 🧪 اختبارات إضافية

### **Test 1: رسالة بسيطة**
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
      "conversation": "مرحبا"
    },
    "messageTimestamp": 1737565200,
    "pushName": "Test User"
  }
}
```

### **Test 2: سؤال للذكاء الاصطناعي**
```json
{
  "event": "messages.upsert",
  "instance": "SENDER",
  "data": {
    "key": {
      "remoteJid": "201097752711@s.whatsapp.net",
      "fromMe": false,
      "id": "TEST-002"
    },
    "message": {
      "conversation": "ما هي عاصمة مصر؟"
    },
    "messageTimestamp": 1737565200,
    "pushName": "Ahmed"
  }
}
```

### **Test 3: رسالة قصيرة**
```json
{
  "event": "messages.upsert",
  "instance": "SENDER",
  "data": {
    "key": {
      "remoteJid": "201097752711@s.whatsapp.net",
      "fromMe": false,
      "id": "TEST-003"
    },
    "message": {
      "conversation": "السلام عليكم"
    },
    "messageTimestamp": 1737565200,
    "pushName": "Sara"
  }
}
```

---

## ⚠️ ملاحظة مهمة

**المشكلة الحالية:** الـ workflow فيه خطأ في Reply API node (الـ `=` في jsonBody)

**الحلول:**

### **الحل 1: استورد الـ workflow المصحح**
1. ارفع الملف الجديد: `G777_FIXED_V2.json`
2. استورده في n8n
3. فعّله
4. جرب الاختبار

### **الحل 2: صلّح الـ workflow يدوياً في n8n**
1. افتح workflow G777 في n8n
2. اضغط على node "Reply API"
3. في Body Parameters:
   - غيّر من Expression إلى JSON
   - أو احذف الـ `=` من أول الـ expression

---

## 🎯 الخطوات

1. **جرب الـ JSON أعلاه في Postman**
2. **إذا حصلت على 500 Error:**
   - المشكلة في الـ workflow
   - استورد `G777_FIXED_V2.json`
3. **إذا حصلت على 200 OK:**
   - تحقق من n8n Executions
   - شاهد إذا Reply API نجح

---

**جرب دلوقتي وقولي النتيجة!** 🚀

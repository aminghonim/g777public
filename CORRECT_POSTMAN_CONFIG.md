# ✅ الإعدادات الصحيحة المحدثة - بناءً على G777_FIXED.json

## 🎯 الـ JSON الصحيح 100%

بناءً على الـ workflow الفعلي (G777_FIXED.json):

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

### **Body (raw - JSON):**

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
    "pushName": "Test User"
  }
}
```

---

## 🔑 النقاط المهمة

### **1. instance:**
```json
"instance": "SENDER"
```
✅ **يجب أن يكون "SENDER"** - هذا هو الاسم المستخدم في Evolution API

### **2. remoteJid:**
```json
"remoteJid": "201234567890@s.whatsapp.net"
```
✅ **رقم الهاتف + @s.whatsapp.net** - هذا هو التنسيق الصحيح لـ WhatsApp

### **3. fromMe:**
```json
"fromMe": false
```
✅ **يجب أن يكون false** - لأن الرسالة من المستخدم، ليست من البوت

---

## 🧪 أمثلة الاختبار الصحيحة

### **Test 1: رسالة بسيطة**
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
      "remoteJid": "201234567890@s.whatsapp.net",
      "fromMe": false,
      "id": "TEST-002"
    },
    "message": {
      "conversation": "ما هي عاصمة مصر؟"
    },
    "pushName": "Ahmed"
  }
}
```

### **Test 3: رسالة مع Emoji**
```json
{
  "event": "messages.upsert",
  "instance": "SENDER",
  "data": {
    "key": {
      "remoteJid": "201234567890@s.whatsapp.net",
      "fromMe": false,
      "id": "TEST-003"
    },
    "message": {
      "conversation": "مرحبا! 😊🎉 كيف حالك؟"
    },
    "pushName": "Sara"
  }
}
```

### **Test 4: رسالة طويلة**
```json
{
  "event": "messages.upsert",
  "instance": "SENDER",
  "data": {
    "key": {
      "remoteJid": "201234567890@s.whatsapp.net",
      "fromMe": false,
      "id": "TEST-004"
    },
    "message": {
      "conversation": "أريد أن أعرف كل شيء عن الذكاء الاصطناعي وكيف يعمل"
    },
    "pushName": "Mohamed"
  }
}
```

---

## 📊 تحليل الـ Workflow

بناءً على `G777_FIXED.json`:

### **Reply API Node:**
```json
"url": "http://127.0.0.1:8080/message/sendText/SENDER"
```
✅ هذا يؤكد أن instance name هو **SENDER**

### **Filter Me Node:**
```javascript
const phone = body.key?.remoteJid;
const fromMe = body.key?.fromMe;

// Filter: not from bot and has text
if (fromMe === true || !message) return [];

// Clean phone number (remove @s.whatsapp.net)
const cleanPhone = phone ? phone.replace('@s.whatsapp.net', '') : phone;
```
✅ هذا يؤكد أن:
- `remoteJid` يجب أن يحتوي على `@s.whatsapp.net`
- `fromMe` يجب أن يكون `false`

---

## ✅ Checklist النهائي

- [ ] **instance = "SENDER"** (مش "default") ✅
- [ ] **remoteJid = "رقم@s.whatsapp.net"** ✅
- [ ] **fromMe = false** ✅
- [ ] **message.conversation = "النص"** ✅
- [ ] **URL = /webhook/whatsapp** (مش /webhook-test/) ✅
- [ ] **n8n Workflow Active** ✅

---

## 🎯 الخلاصة

**الفرق الرئيسي:**
```json
❌ "instance": "default"     // خطأ!
✅ "instance": "SENDER"       // صح!
```

**استخدم الإعدادات أعلاه بالظبط!** 🚀

---

**آسف على الخطأ! جرب دلوقتي بالإعدادات الصحيحة!** 😊

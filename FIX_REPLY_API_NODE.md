# 🔧 إصلاح Reply API Node في n8n

## ❌ المشكلة الحالية:

في Reply API node، الـ Body Parameters فيها:

```
={
  "number": "{{ $('Filter Me').item.json.phone }}",
  "text": "{{ $('AI Agent').item.json.output }}"
}
```

**المشكلة:** الـ `=` في الأول بيخلي n8n يفكر إنه expression لكن الـ syntax غلط!

---

## ✅ الحل:

### **الطريقة 1: استخدام JSON (الأفضل)**

1. افتح n8n workflow **G777**
2. اضغط على node **"Reply API"**
3. في الـ panel اليمين:
   - **Body** → اختر **JSON**
   - في الـ JSON field، احذف كل حاجة واكتب:

```json
{
  "number": "={{ $('Filter Me').item.json.phone }}",
  "text": "={{ $('AI Agent').item.json.output }}"
}
```

**ملاحظة:** الـ `={{` داخل الـ string، مش قبل الـ `{`

---

### **الطريقة 2: استخدام Expression**

1. افتح node **"Reply API"**
2. **Body** → اختر **Expression**
3. في الـ Expression field:

```javascript
{
  "number": $('Filter Me').item.json.phone,
  "text": $('AI Agent').item.json.output
}
```

**ملاحظة:** بدون quotes حوالين الـ expressions، وبدون `=` في الأول

---

### **الطريقة 3: استخدام Parameters (الأسهل)**

1. افتح node **"Reply API"**
2. **Body** → اختر **Body Parameters**
3. اضغط **Add Parameter** مرتين:

**Parameter 1:**
- Name: `number`
- Value: اضغط على الأيقونة واختر Expression
- Expression: `{{ $('Filter Me').item.json.phone }}`

**Parameter 2:**
- Name: `text`
- Value: اضغط على الأيقونة واختر Expression
- Expression: `{{ $('AI Agent').item.json.output }}`

---

## 🎯 الحل الموصى به (الطريقة 1)

**في Reply API node:**

### **Settings:**
- **Method:** POST
- **URL:** `http://127.0.0.1:8080/message/sendText/SENDER`

### **Headers:**
- `Content-Type`: `application/json`
- `apikey`: `{{EVOLUTION_API_KEY}}`

### **Body:**
اختر **JSON** واكتب:

```json
{
  "number": "={{ $('Filter Me').item.json.phone }}",
  "text": "={{ $('AI Agent').item.json.output }}"
}
```

---

## 📸 كيف يجب أن يبدو:

```
Reply API Node Settings:
├─ Method: POST
├─ URL: http://127.0.0.1:8080/message/sendText/SENDER
├─ Headers:
│  ├─ Content-Type: application/json
│  └─ apikey: {{EVOLUTION_API_KEY}}
└─ Body (JSON):
   {
     "number": "={{ $('Filter Me').item.json.phone }}",
     "text": "={{ $('AI Agent').item.json.output }}"
   }
```

---

## ✅ بعد التعديل:

1. **احفظ** الـ workflow (Save)
2. تأكد أن الـ workflow **Active** (أخضر)
3. **جرب من Postman تاني**

---

## 🧪 الاختبار:

بعد التعديل، جرب الـ JSON ده في Postman:

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

**المتوقع:** 200 OK ✅

---

**صلّح الـ Reply API node وجرب تاني!** 🚀

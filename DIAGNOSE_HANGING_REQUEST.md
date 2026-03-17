# 🔍 تشخيص المشكلة - Request معلق

## ❓ المشكلة:
الـ request من Postman **معلق** (بياخد وقت طويل جداً)

---

## 🎯 الأسباب المحتملة:

### **1. Gemini API بطيء أو مش شغال**
- الـ AI Agent node بيستنى رد من Gemini
- Gemini API قد يكون بطيء أو الـ API Key غلط

### **2. Reply API node فيه مشكلة**
- لو الـ JSON body لسه غلط، الـ node هيفضل يحاول
- أو Evolution API مش بيرد

### **3. Memory node واقف**
- Simple Memory node قد يكون بيحاول يحفظ البيانات وواقف

---

## ✅ الحلول:

### **الحل 1: تبسيط الـ Workflow (للاختبار)**

**حذف الـ nodes المعقدة مؤقتاً:**

1. افتح n8n workflow **G777**
2. **احذف** الـ connections التالية مؤقتاً:
   - AI Agent → Reply API (احذف الـ connection)
3. **أضف** connection جديد:
   - Filter Me → Reply API (مباشرة)
4. **عدّل Reply API node:**
   - Body:
   ```json
   {
     "number": "={{ $('Filter Me').item.json.phone }}",
     "text": "تم استلام رسالتك: {{ $('Filter Me').item.json.message }}"
   }
   ```
5. **احفظ** واختبر

**هذا سيتخطى Gemini ويرد مباشرة - للتأكد أن المشكلة في Gemini**

---

### **الحل 2: تحقق من Gemini API Key**

1. افتح n8n workflow
2. اضغط على **Google Gemini Chat Model** node
3. تحقق من الـ Credential:
   - هل الـ API Key صحيح؟
   - جرب API Key جديد من: https://aistudio.google.com/app/apikey

---

### **الحل 3: زيادة Timeout**

في Postman:
- Settings → Request timeout → زوّده لـ 60 seconds

في PowerShell:
```powershell
Invoke-RestMethod -Uri $url -Method POST -Body $json -ContentType "application/json" -TimeoutSec 60
```

---

### **الحل 4: اختبار بدون AI (الأسرع)**

**workflow بسيط للاختبار:**

```
WhatsApp Webhook → Filter Me → Reply API
```

**Reply API Body:**
```json
{
  "number": "={{ $('Filter Me').item.json.phone }}",
  "text": "مرحباً! تم استلام رسالتك"
}
```

**هذا سيختبر الـ workflow بدون Gemini**

---

## 🎯 الخطوة التالية:

### **اختبار سريع:**

1. **افتح n8n**
2. **عدّل Reply API node** ليرد برسالة ثابتة (بدون AI)
3. **احفظ**
4. **جرب من Postman**

**إذا نجح:** المشكلة في Gemini API
**إذا لسه معلق:** المشكلة في Reply API أو Evolution API

---

## 📋 Workflow مبسط للاختبار:

```json
{
  "number": "201097752711",
  "text": "تم استلام رسالتك بنجاح!"
}
```

ضع هذا في Reply API node (بدون expressions) واختبر.

---

**جرب الحل 1 (تبسيط الـ workflow) وقولي النتيجة!** 🚀

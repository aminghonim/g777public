# 🔧 إعدادات عقدة Supabase في n8n - نسخ ولصق

## 📋 عقدة: Supabase Fetch Memory

### **1. أضف Node جديد:**
- في n8n workflow (G777)
- بعد **Filter Me** node
- قبل **AI Agent** node
- اضغط **"+"** → اختر **"HTTP Request"**

---

### **2. الإعدادات الأساسية:**

#### **Node Name:**
```
Supabase Fetch Memory
```

#### **Method:**
```
GET
```

#### **URL:**
انسخ هذا بالظبط:
```
https://lsrtcishnwohbjonshxk.supabase.co/rest/v1/customer_memory?phone=eq.{{ $('Filter Me').item.json.phone }}&select=*&order=created_at.desc&limit=5
```

**ملاحظة:** لازم تكون Expression! اضغط على أيقونة fx بجانب URL field

---

### **3. Headers:**

اضغط **"Add Header"** مرتين:

#### **Header 1:**
```
Name: apikey
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzcnRjaXNobndvaGJqb25zaHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjQ3MDYsImV4cCI6MjA4NDA0MDcwNn0.y5xoy-wu7yFlHUdmd0MMp4BpiI6NKNCEwxY1CSfhVpI
```

#### **Header 2:**
```
Name: Authorization
Value: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzcnRjaXNobndvaGJqb25zaHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjQ3MDYsImV4cCI6MjA4NDA0MDcwNn0.y5xoy-wu7yFlHUdmd0MMp4BpiI6NKNCEwxY1CSfhVpI
```

---

### **4. Options:**

- **Continue On Fail:** ON (مفعّل)

---

### **5. Connection:**

#### **Input:**
```
Filter Me → Supabase Fetch Memory
```

#### **Output:**
```
Supabase Fetch Memory → AI Agent
```

---

## 📸 الشكل النهائي:

```
┌─────────────────────────────────────┐
│ HTTP Request                        │
│ Name: Supabase Fetch Memory         │
├─────────────────────────────────────┤
│ Method: GET                         │
│                                     │
│ URL: (Expression)                   │
│ https://lsrtcishnwohbjonshxk...     │
│ ...?phone=eq.{{ $('Filter Me')...   │
│                                     │
│ Headers:                            │
│ ┌─────────────┬─────────────────┐  │
│ │ apikey      │ eyJhbGci...     │  │
│ │ Authorization│ Bearer eyJh... │  │
│ └─────────────┴─────────────────┘  │
│                                     │
│ Options:                            │
│ ☑ Continue On Fail                 │
└─────────────────────────────────────┘
```

---

## ✅ للنسخ السريع:

### **URL (Expression):**
```
https://lsrtcishnwohbjonshxk.supabase.co/rest/v1/customer_memory?phone=eq.{{ $('Filter Me').item.json.phone }}&select=*&order=created_at.desc&limit=5
```

### **apikey Header:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzcnRjaXNobndvaGJqb25zaHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjQ3MDYsImV4cCI6MjA4NDA0MDcwNn0.y5xoy-wu7yFlHUdmd0MMp4BpiI6NKNCEwxY1CSfhVpI
```

### **Authorization Header:**
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzcnRjaXNobndvaGJqb25zaHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjQ3MDYsImV4cCI6MjA4NDA0MDcwNn0.y5xoy-wu7yFlHUdmd0MMp4BpiI6NKNCEwxY1CSfhVpI
```

---

## 🎯 بعد الإضافة:

1. **احفظ** الـ workflow
2. **اختبر** من Postman
3. **شاهد** النتيجة في n8n Executions

---

**أضف الـ node ده واملأ البيانات، وقولي لما تخلص!** 🚀

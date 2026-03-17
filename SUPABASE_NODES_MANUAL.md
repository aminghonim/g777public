# 🔧 إعدادات Supabase Nodes في n8n - يدوياً

## 📋 Node 1: Supabase Fetch Memory

### **Node Type:**
```
HTTP Request
```

### **الإعدادات:**

#### **Method:**
```
GET
```

#### **URL:**
```
=https://lsrtcishnwohbjonshxk.supabase.co/rest/v1/customer_memory?phone=eq.{{ $json.phone }}&select=*&order=created_at.desc&limit=5
```

#### **Headers:**
اضغط **Add Parameter** مرتين:

**Header 1:**
- Name: `apikey`
- Value: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzcnRjaXNobndvaGJqb25zaHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjQ3MDYsImV4cCI6MjA4NDA0MDcwNn0.y5xoy-wu7yFlHUdmd0MMp4BpiI6NKNCEwxY1CSfhVpI`

**Header 2:**
- Name: `Authorization`
- Value: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzcnRjaXNobndvaGJqb25zaHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjQ3MDYsImV4cCI6MjA4NDA0MDcwNn0.y5xoy-wu7yFlHUdmd0MMp4BpiI6NKNCEwxY1CSfhVpI`

#### **Options:**
- **On Error:** Continue on Error

---

## 📋 Node 2: Supabase Save Memory

### **Node Type:**
```
HTTP Request
```

### **الإعدادات:**

#### **Method:**
```
POST
```

#### **URL:**
```
https://lsrtcishnwohbjonshxk.supabase.co/rest/v1/customer_memory
```

#### **Headers:**
اضغط **Add Parameter** 4 مرات:

**Header 1:**
- Name: `apikey`
- Value: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzcnRjaXNobndvaGJqb25zaHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjQ3MDYsImV4cCI6MjA4NDA0MDcwNn0.y5xoy-wu7yFlHUdmd0MMp4BpiI6NKNCEwxY1CSfhVpI`

**Header 2:**
- Name: `Authorization`
- Value: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzcnRjaXNobndvaGJqb25zaHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjQ3MDYsImV4cCI6MjA4NDA0MDcwNn0.y5xoy-wu7yFlHUdmd0MMp4BpiI6NKNCEwxY1CSfhVpI`

**Header 3:**
- Name: `Content-Type`
- Value: `application/json`

**Header 4:**
- Name: `Prefer`
- Value: `return=minimal`

#### **Body:**
- اختر **JSON**
- في الـ JSON field:

```json
{
  "phone": "={{ $('Filter Me').item.json.phone }}",
  "fact": "={{ $('AI Agent').item.json.output }}",
  "customer_name": "Test User",
  "intent": "inquiry"
}
```

#### **Options:**
- **On Error:** Continue on Error

---

## 🎯 ملخص سريع:

### **Supabase Credentials:**
```
URL: https://lsrtcishnwohbjonshxk.supabase.co
API Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzcnRjaXNobndvaGJqb25zaHhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjQ3MDYsImV4cCI6MjA4NDA0MDcwNn0.y5xoy-wu7yFlHUdmd0MMp4BpiI6NKNCEwxY1CSfhVpI
```

### **الجدول:**
```
customer_memory
```

### **الأعمدة:**
- id (SERIAL)
- phone (TEXT)
- customer_name (TEXT)
- fact (TEXT)
- intent (TEXT)
- created_at (TIMESTAMP)

---

## 📸 كيف يبدو في n8n:

```
Filter Me
    ↓
[HTTP Request - Supabase Fetch]
    ↓
AI Agent
    ↓
[HTTP Request - Supabase Save]
    ↓
Reply API
```

---

**ابدأ بإنشاء الجدول في Supabase أولاً، ثم أضف الـ nodes!** 🚀

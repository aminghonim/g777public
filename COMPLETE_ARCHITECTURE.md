# 🏗️ G777 Project Architecture - Complete Documentation

> **آخر تحديث:** 2026-01-23
> **الحالة:** ✅ موثق بالكامل

---

## 📊 البنية الكاملة للمشروع

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            G777 ANTIGRAVITY SUITE                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌───────────────────────────────────────────────────────────────────────────┐    │
│   │                         LOCAL MACHINE (جهازك)                             │    │
│   │                                                                           │    │
│   │   ┌─────────────────────────────────────────────────────────────────┐     │    │
│   │   │    ANTIGRAVITY SUITE (python main.py)                          │     │    │
│   │   │    Port 8080                                                    │     │    │
│   │   │                                                                 │     │    │
│   │   │    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │     │    │
│   │   │    │  NiceGUI    │  │  Backend    │  │  AI Engine  │           │     │    │
│   │   │    │  (UI)       │  │  (FastAPI)  │  │  (Gemini)   │           │     │    │
│   │   │    └─────────────┘  └─────────────┘  └─────────────┘           │     │    │
│   │   │                                                                 │     │    │
│   │   └─────────────────────────────────────────────────────────────────┘     │    │
│   │                                                                           │    │
│   └───────────────────────────────────────────────────────────────────────────┘    │
│                                         │                                          │
│                                         │ HTTP Requests                            │
│                                         ▼                                          │
│   ┌───────────────────────────────────────────────────────────────────────────┐    │
│   │                    AZURE VM (127.0.0.1) - السحابة                       │    │
│   │                                                                           │    │
│   │   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐        │    │
│   │   │  EVOLUTION API  │   │  BAILEYS        │   │     N8N         │        │    │
│   │   │  Port 8080      │   │  SERVICE        │   │   Port 5678     │        │    │
│   │   │                 │   │  Port 3000      │   │                 │        │    │
│   │   │  WhatsApp       │   │  WhatsApp       │   │  Workflow       │        │    │
│   │   │  Business API   │   │  Web API        │   │  Automation     │        │    │
│   │   └────────┬────────┘   └────────┬────────┘   └────────┬────────┘        │    │
│   │            │                     │                     │                  │    │
│   │            └─────────────────────┴─────────────────────┘                  │    │
│   │                         شبكة داخلية واحدة                                │    │
│   └───────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 الفرق بين الخدمات الثلاثة (مهم جداً!)

### 1️⃣ **Evolution API** (Port 8080)
```yaml
الوظيفة: WhatsApp Business API المتقدم
المميزات:
  - إدارة Instances متعددة
  - Webhook متقدم
  - دعم الـ Media
  - REST API شامل
  - إدارة QR Codes
  
الاستخدام في المشروع:
  - cloud_service.py يستخدمها للتواصل مع WhatsApp من الـ UI
  - pairing_page.py يستخدمها لعرض QR Code وربط الحساب
  
الـ Endpoints:
  - GET  /instance/connect/{instance}     → QR Code
  - GET  /instance/connectionState/{instance} → حالة الاتصال
  - POST /message/sendText/{instance}     → إرسال رسالة
  - POST /webhook/set/{instance}          → ضبط Webhook
```

### 2️⃣ **Baileys Service** (Port 3000)
```yaml
الوظيفة: WhatsApp Web API خفيف (مبني على Baileys)
المميزات:
  - خفيف وسريع
  - QR Code مباشر
  - إرسال رسائل بسيط
  - لا يحتاج Instance management
  
الاستخدام في المشروع:
  - baileys_client.py يستخدمها لإرسال الردود من الـ Backend
  - webhook_handler.py يستقبل الرسائل منها
  
الـ Endpoints:
  - GET  /health     → فحص الصحة
  - GET  /status     → حالة الاتصال
  - GET  /qr         → QR Code data
  - GET  /qr-image   → QR كصفحة HTML
  - POST /send       → إرسال رسالة
```

### 3️⃣ **N8N** (Port 5678)
```yaml
الوظيفة: Workflow Automation (أتمتة المهام)
المميزات:
  - No-code/Low-code
  - AI Agent Integration
  - ذاكرة محادثة
  - تكامل مع Gemini
  
الاستخدام في المشروع:
  - بديل لـ AI Engine في الـ Backend
  - يستقبل Webhook من Evolution API
  - يعالج الرسائل بـ Gemini
  - يرد عبر Evolution API
  
الـ Flow:
  Webhook → Filter Me → AI Agent + Memory → Reply API
```

---

## 🎯 لماذا يوجد خدمتان للواتساب؟

### **السيناريو الحالي (ده اللي حصل معاك):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   📱 تطبيق WhatsApp على الموبايل                                           │
│                      │                                                      │
│                      │ Linked Device                                        │
│                      ▼                                                      │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │      "Google Chrome (Baileys)"      ← ⚠️ هذا ما يظهر!           │      │
│   │      هذا معناه أن Baileys Service هي المتصلة                   │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **لماذا؟**

| الخدمة | مصدر الربط | ما يظهر على الموبايل |
|--------|-----------|---------------------|
| **Baileys Service** | عبر `python main.py` (pairing_page.py) | "Google Chrome (Baileys)" |
| **Evolution API** | عبر لوحة تحكم Evolution | "Windows" أو اسم الـ Instance |

### **الخلاصة:**

لما شغلت `python main.py` وربطت الواتساب من صفحة Pairing:
1. ✅ **cloud_service.py** تواصل مع **Evolution API** لجلب QR Code
2. ✅ لكن **Evolution API** داخلياً تستخدم **Baileys** كـ engine!
3. ✅ لذلك يظهر على الموبايل **"Google Chrome (Baileys)"**

---

## 🏗️ البنية الصحيحة للمشروع

### **المسار 1: من الـ UI (python main.py)**

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│   👤 المستخدم يستخدم الـ UI (NiceGUI)                                     │
│            ↓                                                               │
│   📱 pairing_page.py                                                       │
│            ↓                                                               │
│   🔧 cloud_service.py (يتواصل مع Evolution API)                           │
│            ↓                                                               │
│   🌐 Evolution API (Port 8080 على Azure)                                  │
│            ↓                                                               │
│   📲 WhatsApp يتصل                                                        │
│            ↓                                                               │
│   يظهر على الموبايل: "Google Chrome (Baileys)"                            │
│                                                                            │
│   ⚠️ هذا طبيعي! لأن Evolution API تستخدم Baileys داخلياً                  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### **المسار 2: استقبال الرسائل ومعالجتها**

#### **Option A: عبر Backend (الكود الحالي)**
```
WhatsApp رسالة ← Baileys Service ← webhook_handler.py ← AI Engine ← رد
                    (Port 3000)       (Port 8080)      (Gemini)
```

#### **Option B: عبر N8N (الأتمتة)**
```
WhatsApp رسالة ← Evolution API ← N8N Webhook ← AI Agent ← Reply API ← رد
                  (Port 8080)   (Port 5678)   (Gemini)
```

---

## ❓ أي مسار تستخدم؟

### **الإجابة:**

من تحليل الكود الحالي:

| الملف | يستخدم | للوظيفة |
|-------|--------|---------|
| `cloud_service.py` | Evolution API | Pairing, Send Messages, Campaigns |
| `baileys_client.py` | Baileys Service | Send Replies from Backend |
| `webhook_handler.py` | يستقبل من Baileys | Process Incoming Messages |
| `pairing_page.py` | Evolution API | QR Code, Connection Status |

### **النتيجة:**

**المشروع الحالي يستخدم الاثنين معاً بشكل متكامل!**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   UI (Pairing, Campaigns)                                                   │
│         ↓                                                                   │
│   cloud_service.py ──────→ Evolution API (Port 8080)                       │
│                                    │                                        │
│                                    ↓                                        │
│                        ┌──────────────────────┐                            │
│                        │   WhatsApp Web        │                            │
│                        │   (Baileys Engine)    │                            │
│                        └──────────────────────┘                            │
│                                    │                                        │
│   رسالة واردة                    ↓                                        │
│                        Baileys Service (Port 3000)                         │
│                                    ↓                                        │
│   webhook_handler.py ←── Webhook POST /webhook/whatsapp                    │
│         ↓                                                                   │
│   ai_engine.py (Gemini)                                                    │
│         ↓                                                                   │
│   baileys_client.py ─────→ Baileys Service (/send)                         │
│         ↓                                                                   │
│   رد للعميل 📤                                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚠️ مشكلة الـ Error Handler

الـ Error الذي ظهر في الصورة:
```
status: ERROR
errorType: CONNECTION_FAILED
errorMessage: Cannot connect to Evolution API
```

**السبب:**
- n8n Workflow يحاول إرسال رسالة عبر Evolution API
- لكن الـ Webhook في Evolution API مش مضبوط صح
- أو الـ Instance مش connected

**الحل:**
تم ضبط الـ Webhook بنجاح. الآن محتاج:
1. ✅ التأكد من اتصال WhatsApp (Scan QR)
2. ✅ التأكد من أن n8n Workflow مفعّل

---

## 🔧 الإعدادات الصحيحة

### **Evolution API Webhook:**
```json
{
  "enabled": true,
  "url": "http://localhost:5678/webhook/whatsapp",
  "events": ["MESSAGES_UPSERT"]
}
```

### **N8N Reply API Node:**
```yaml
URL: http://localhost:8080/message/sendText/SENDER
Headers:
  - apikey: {{EVOLUTION_API_KEY}}
Body:
  - number: {{ $('Filter Me').item.json.phone }}
  - text: {{ $('AI Agent').item.json.output }}
```

### **Baileys Service Environment:**
```env
PORT=3000
WEBHOOK_URL=http://localhost:8080/webhook/whatsapp
```

---

## 🎯 الخلاصة النهائية

### **لا يوجد تعارض!**

الخدمتين (Baileys + Evolution) **مكملتين لبعض**:

| الخدمة | الدور |
|--------|-------|
| **Evolution API** | API Layer (REST interface لـ WhatsApp) |
| **Baileys Service** | Engine Layer (الاتصال الفعلي بـ WhatsApp) |
| **N8N** | Automation Layer (معالجة الرسائل بالذكاء الاصطناعي) |

**هذا التصميم ممتاز لأنه:**
1. ✅ يفصل بين الطبقات (Separation of Concerns)
2. ✅ يسمح باستخدام أي طريقة للتواصل (UI أو API)
3. ✅ يدعم الأتمتة عبر n8n
4. ✅ يعمل 24/7 على السحابة

---

## 📋 ملخص الـ Ports

| Port | الخدمة | الوظيفة |
|------|--------|---------|
| **8080** (Azure) | Evolution API | WhatsApp Business API |
| **3000** (Azure) | Baileys Service | WhatsApp Web Engine |
| **5678** (Azure) | N8N | Workflow Automation |
| **8080** (Local) | Antigravity Suite | UI + Backend |

---

**✅ فهمت البنية الآن؟** 🎉

# 🦅 G777 Git Workflow Guide

هذا الدليل يشرح كيفية استخدام سكريبت الأتمتة `git_auto.ps1` للعمل بنظام احترافي ومنضبط.

## 🌟 المبادئ الأساسية
1. **العزل (Isolation):** لا عمل مباشر على `main` أبداً.
2. **التوثيق (Documentation):** كل تغيير له رسالة واضحة.
3. **التحقق (Verification):** الدمج يتم فقط بعد التأكد.

---

## 🛠️ الأوامر

### 1️⃣ بدء ميزة جديدة (Start Feature)
يستخدم لإنشاء فرع جديد وسحب آخر التحديثات.

```powershell
.\git_auto.ps1 -Command Start -Name "اسم-الميزة"
```
مثال:
```powershell
.\git_auto.ps1 -Command Start -Name "fix-whatsapp-qr"
```
*النتيجة:* ينقلك لفرع `feature/fix-whatsapp-qr`.

---

### 2️⃣ حفظ العمل (Save Work)
يستخدم لعمل Commit و Push للفرع الحالي.

```powershell
.\git_auto.ps1 -Command Save -Message "وصف التغيير"
```
مثال:
```powershell
.\git_auto.ps1 -Command Save -Message "Updated cloud_service.py to auto-logout on stale session"
```

---

### 3️⃣ إنهاء الميزة (Finish Feature)
يستخدم لدمج الفرع الحالي في `main` وحذفه.

```powershell
.\git_auto.ps1 -Command Finish
```
*سيطلب منك التأكيد (y/n) قبل الدمج.*

---

## ⚠️ ملاحظات هامة
- السكريبت سيمنعك من الحفظ إذا كنت على `main` بالخطأ.
- السكريبت يقوم بعمل `git stash` تلقائياً إذا كان لديك تغييرات غير محفوظة عند بدء ميزة جديدة.

# G777 Nightly Analyst - دليل التشغيل
================================

## 📋 الوصف
المحلل الليلي هو سكربت بايثون يعمل تلقائياً كل يوم الساعة 3 صباحاً لتحليل محادثات اليوم واستخراج:
- أكثر الأسئلة شيوعاً (Top Intents)
- الأسئلة التي فشل البوت في الإجابة عليها
- اقتراحات لتحسين الأداء

## 🚀 التثبيت على السيرفر

### الطريقة الأولى: تثبيت آلي (موصى به)

1. **رفع الكود للسيرفر:**
```bash
cd D:\WORK\2
git add .
git commit -m "Add Nightly Analyst Script"
git push origin main
```

2. **التشغيل المحلي:**
```bash
cd /path/to/project
```

3. **تحديث الكود:**
```bash
git pull
```

4. **تشغيل سكربت الإعداد:**
```bash
chmod +x scripts/setup_nightly_analyst.sh
./scripts/setup_nightly_analyst.sh
```

---

### الطريقة الثانية: تثبيت يدوي

1. **تثبيت المتطلبات:**
```bash
pip3 install psycopg2-binary google-generativeai python-dotenv
```

2. **إعطاء صلاحيات التنفيذ:**
```bash
chmod +x scripts/nightly_analyst.py
```

3. **إضافة Cron Job:**
```bash
crontab -e
```

أضف السطر التالي:
```
0 3 * * * cd /path/to/project && /usr/bin/python3 scripts/nightly_analyst.py >> logs/nightly_analyst.log 2>&1
```

---

## 🧪 التشغيل التجريبي (قبل الجدولة)

لتشغيل السكربت يدوياً للتأكد من عمله:

```bash
cd /path/to/project
python3 scripts/nightly_analyst.py
```

---

## 📊 مراجعة النتائج

### 1. في قاعدة البيانات (Supabase):
افتح Supabase → SQL Editor → نفذ:
```sql
SELECT * FROM g777_training_insights ORDER BY created_at DESC LIMIT 5;
```

### 2. في اللوجات:
```bash
tail -f logs/nightly_analyst.log
```

---

## ⚙️ المتغيرات البيئية المطلوبة

تأكد من وجود المتغيرات التالية في ملف `.env`:

```env
DATABASE_URL=postgresql://user:password@host:port/database
GEMINI_API_KEY=your_gemini_api_key_here
ADMIN_PHONE=+201234567890  # اختياري - لإرسال التقارير
```

---

## 🔧 استكشاف الأخطاء

### المشكلة: السكربت لا يعمل
**الحل:**
```bash
# تحقق من اللوجات
cat logs/nightly_analyst.log

# تحقق من Cron Jobs
crontab -l
```

### المشكلة: خطأ في الاتصال بقاعدة البيانات
**الحل:**
تأكد من صحة `DATABASE_URL` في ملف `.env`

### المشكلة: خطأ في Gemini API
**الحل:**
تأكد من صحة `GEMINI_API_KEY` وأن لديك Quota متاح

---

## 📅 جدولة مخصصة

لتغيير وقت التشغيل، عدّل Cron Job:

```bash
crontab -e
```

أمثلة:
- كل ساعة: `0 * * * *`
- كل 6 ساعات: `0 */6 * * *`
- كل يوم الساعة 2 صباحاً: `0 2 * * *`

---

## 🎯 الخطوات التالية

بعد تشغيل المحلل لعدة أيام:
1. راجع جدول `g777_training_insights`
2. اقرأ الاقتراحات المستخرجة
3. طبّق التحسينات على System Prompt
4. ضع علامة `applied = TRUE` على التحسينات المطبقة

---

**آخر تحديث:** 2026-01-27
**الإصدار:** 1.0

# نظام التوجيه الذكي الموحد (Smart Unified Routing System)

**التاريخ:** 2026-03-11  
**المطور:** CNS Squad - AI & RAG Engineer  
**الحالة:** ✅ مصممة وجاهزة للتنفيذ

## 📋 ملخص التحليل

تم تحليل العلاقة بين `backend/ai_client.py` (UnifiedAIClient) و `backend/core/model_router.py` لتصميم نظام توجيه ذكي موحد.

## 🔍 التحليل الحالي

### 1. **UnifiedAIClient** (ai_client.py)
- **الوظيفة:** موحد بين Gemini و Claude
- **الافتيار التلقائي:** Gemini → Claude
- **نقطة الضعف:** لا يوجد تمرير لحالة المزود (Provider Health)
- **التبديل:** يدوي فقط عند الفشل

### 2. **ModelRouter** (model_router.py)
- **الوظيفة:** اختيار النموذج حسب نوع المهمة
- **الترتيب:** DB Override → Config Task → Default → Hardcoded
- **القوة:** ديناميكي وقابل للتكوين
- **النقص:** لا يرتبط مباشرة بـ UnifiedAIClient

### 3. **QuotaGuard** (quota_guard.py)
- **الوظيفة:** حصص استخدام الـ API لكل عميل (Tenant)
- **التحقق:** الرسائل اليومية وعدد الحالات
- **الربط:** مع database_manager للحصول على معلومات الحصص

## 🎯 المواصفات المقترحة للنظام الموحد

### **المكون الرئيسي: SmartTaskRouter**

```python
class SmartTaskRouter:
    """
    نظام توجيه ذكي موحد يجمع بين UnifiedAIClient و ModelRouter
    مع دعم التبديل التلقائي وحساب الاستهلاك
    """
```

## 🔄 مسار الفشل (Failure Path)

### **المرحلة 1: التحقق من صحة المزود (Provider Health)**
```python
async def check_provider_health(self, provider: str) -> Dict[str, Any]:
    """
    التحقق من صحة مزود الخدمة
    - إرسال طلب اختبار بسيط
    - قياس زمن الاستجابة
    - التحقق من الحصص المتبقية
    """
```

### **المرحلة 2: التبديل التلقائي الذكي**
```python
async def smart_fallback(self, task: str, current_provider: str) -> str:
    """
    التبديل التلقائي بناءً على:
    - صحة المزود الحالي
    - الحصص المتبقية للعميل
    - متطلبات المهمة
    - تكوين النموذج
    """
```

### **المرحلة 3: تتبع الاستهلاك (Quota Tracking)**
```python
async def track_quota_consumption(self, tenant_id: str, provider: str, tokens: int):
    """
    تتبع استهلاك الـ API لكل عميل
    - تحديث قاعدة البيانات
    - حساب التكلفة
    - إشعارات القرب من الحد الأقصى
    """
```

## 🏗️ الهيكل المقترح

### **1. تكامل UnifiedAIClient مع ModelRouter**
```python
class EnhancedUnifiedAIClient:
    def __init__(self):
        self.unified_client = UnifiedAIClient()
        self.model_router = model_router
        self.quota_guard = QuotaGuard()
        
    async def generate_response_smart(
        self, 
        task: str, 
        prompt: str, 
        tenant_id: str,
        system_message: str = ""
    ) -> Dict[str, Any]:
        """
        توليد استجابة ذكية مع:
        - اختيار النموذج المناسب
        - التبديل التلقائي عند الفشل
        - تتبع الاستهلاك
        """
```

### **2. نظام التبديل التلقائي**
```python
class ProviderHealthManager:
    def __init__(self):
        self.providers = {
            "gemini": {"health": "unknown", "last_check": None},
            "claude": {"health": "unknown", "last_check": None}
        }
    
    async def get_best_provider(self, task: str, tenant_id: str) -> str:
        """
        اختيار أفضل مزود بناءً على:
        - الصحة الحالية
        - الحصص المتبقية
        - متطلبات المهمة
        """
```

### **3. تكامل QuotaGuard**
```python
class SmartQuotaManager:
    async def check_and_consume(
        self, 
        tenant_id: str, 
        provider: str, 
        estimated_tokens: int
    ) -> bool:
        """
        التحقق من الحصص واستهلاك الرسالة
        - التحقق من الحد اليومي
        - حساب التكلفة المتوقعة
        - تحديث العداد
        """
```

## 📊 تدفق البيانات المقترح

```
📱 رسالة WhatsApp
    ↓
🧠 SmartTaskRouter
    ↓
🔍 تحليل المهمة (ModelRouter)
    ↓
💊 التحقق من صحة المزود (Provider Health)
    ↓
🎯 اختيار المزود الأنسب
    ↓
📊 التحقق من الحصص (QuotaGuard)
    ↓
🤖 توليد الاستجابة (UnifiedAIClient)
    ↓
📈 تتبع الاستهلاك
    ↓
📤 الاستجابة النهائية
```

## 🔧 الخوارزميات المقترحة

### **1. خوارزمية الاختيار الذكي**
```python
async def select_provider_algorithm(
    task: str, 
    tenant_id: str, 
    message_urgency: str = "normal"
) -> str:
    """
    أولويات الاختيار:
    1. صحة المزود (Health Check)
    2. الحصص المتبقية (Quota Available)
    3. متطلبات المهمة (Task Requirements)
    4. تكلفة الاستخدام (Cost Efficiency)
    """
```

### **2. خوارزمية التبديل التلقائي**
```python
async def auto_fallback_algorithm(
    failed_provider: str, 
    task: str, 
    tenant_id: str
) -> str:
    """
    منطق التبديل:
    1. التحقق من الأسباب المحتملة للفشل
    2. اختيار البديل الأقرب
    3. تجربة البديل
    4. تسجيل محاولة التبديل
    """
```

### **3. خوارزمية حساب الاستهلاك**
```python
async def calculate_consumption(
    tenant_id: str, 
    provider: str, 
    tokens_used: int,
    model_name: str
) -> Dict[str, Any]:
    """
    حساب الاستهلاك:
    - تكلفة الرموز (Token Cost)
    - خصم الحصص اليومية
    - تحديث الإحصائيات
    - إشعار القرب من الحد
    """
```

## 🛡️ معالجة الأخطاء والمسارات البديلة

### **مسار الفشل الكامل**
```python
async def complete_failure_path(
    task: str, 
    tenant_id: str, 
    error: Exception
) -> str:
    """
    عندما يفشل جميع المزودين:
    1. تسجيل الخطأ الكامل
    2. استخدام رد احتياطي محلي
    3. إشعار المشغل
    4. اقتراح ترقية الخطة
    """
```

### **الردود الاحتياطية**
```python
FALLBACK_RESPONSES = {
    "customer_chat": "عذراً، يواجه نظامنا بعض الصعوبات التقنية. سيتم الرد عليك قريباً.",
    "intent_analysis": {"intent": "unknown", "confidence": 0.0},
    "extraction": {},
    "complex_problem_solving": "يتم تحليل طلبك. يرجى الانتظار قليلاً."
}
```

## 📋 المتطلبات التنفيذية

### **1. تحديث UnifiedAIClient**
- إضافة `health_check()` لكل مزود
- إضافة `get_provider_status()` method
- ربط بـ ModelRouter لاختيار النموذج

### **2. تحسين ModelRouter**
- إضافة `get_provider_for_task()` method
- دعم `tenant_id` في الاختيار
- تكامل مع QuotaGuard

### **3. تعزيز QuotaGuard**
- إضافة `consume_quota()` method
- دعم متعدد المزودين
- حساب التكلفة لكل مزود

### **4. إنشاء SmartTaskRouter**
- يجمع كل المكونات معاً
- يدير التبديل التلقائي
- يوفر واجهة موحدة

## 🎯 الفوائد المتوقعة

### **1. الموثوقية العالية**
- تبديل تلقائي عند الفشل
- تحقق مستمر من صحة المزودين
- مسارات فشل متعددة

### **2. الكفاءة التكلفية**
- اختيار المزود الأقل تكلفة
- تحسين استهلاك الحصص
- إشعارات القرب من الحدود

### **3. المرونة والقابلية للتوسع**
- إضافة مزودين جدد بسهولة
- تكوين ديناميكي
- دعم مهام متخصصة

### **4. الأمان والامتثال**
- عزل البيانات بين العملاء
- التزام بحدود الاستخدام
- تسجيل شامل للعمليات

## 🚀 خارطة التنفيذ

### **المرحلة 1: الأساس (1-2 أيام)**
- تحديث UnifiedAIClient بـ health checks
- تحسين ModelRouter بدعم tenant_id
- تعزيز QuotaGuard بحساب التكلفة

### **المرحلة 2: التكامل (2-3 أيام)**
- إنشاء SmartTaskRouter
- ربط جميع المكونات
- اختبار التبديل التلقائي

### **المرحلة 3: التحسين (1-2 يوم)**
- إضافة الإحصائيات والتقارير
- تحسين الخوارزميات
- اختبار الحمل الثقيل

---

**النتيجة:** نظام توجيه ذكي موحد يجمع بين الموثوقية والكفاءة والمرونة للتعامل مع جميع حالات الاستخدام والفشل.

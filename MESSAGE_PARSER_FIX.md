# 🔧 حل نهائي - Message Parser الصحيح

## 📋 الكود الصحيح 100%:

```javascript
// الحصول على البيانات الواردة
const incoming = $input.first().json;

// البحث عن الرقم في جميع الأماكن الممكنة
let phone = '';
let message = '';
let customerName = 'عميل';

// استخراج الرقم
if (incoming.data && incoming.data.key && incoming.data.key.remoteJid) {
  // من Postman (data.key.remoteJid)
  phone = incoming.data.key.remoteJid;
} else if (incoming.key && incoming.key.remoteJid) {
  // من Evolution API مباشرة
  phone = incoming.key.remoteJid;
} else if (incoming.body && incoming.body.data && incoming.body.data.key) {
  // من webhook body
  phone = incoming.body.data.key.remoteJid;
} else if (incoming.from) {
  // fallback
  phone = incoming.from;
}

// تنظيف الرقم
phone = phone.replace('@c.us', '').replace('@s.whatsapp.net', '');

// استخراج الرسالة
if (incoming.data && incoming.data.message && incoming.data.message.conversation) {
  message = incoming.data.message.conversation;
} else if (incoming.message && incoming.message.conversation) {
  message = incoming.message.conversation;
} else if (incoming.body && incoming.body.data && incoming.body.data.message) {
  message = incoming.body.data.message.conversation;
} else if (incoming.text) {
  message = incoming.text;
}

// استخراج الاسم
if (incoming.data && incoming.data.pushName) {
  customerName = incoming.data.pushName;
} else if (incoming.pushName) {
  customerName = incoming.pushName;
} else if (incoming.body && incoming.body.data && incoming.body.data.pushName) {
  customerName = incoming.body.data.pushName;
}

// إنشاء chatId
const chatId = phone + '@s.whatsapp.net';

// تحديد Intent
let intent = 'inquiry';
if (/حجز|برنامج|رحلة|سفر|عمرة|حج|سياحة|booking|trip|travel/i.test(message)) {
  intent = 'booking';
}

// إرجاع النتيجة
return {
  json: {
    phone: phone,
    message: message,
    customerName: customerName,
    chatId: chatId,
    intent: intent,
    timestamp: new Date().toISOString()
  }
};
```

---

## 🎯 أو استخدم هذا الكود المبسط للاختبار:

```javascript
// كود بسيط جداً للاختبار
const data = $input.first().json;

// استخراج مباشر
const phone = (data.data?.key?.remoteJid || data.key?.remoteJid || '').replace('@s.whatsapp.net', '').replace('@c.us', '');
const message = data.data?.message?.conversation || data.message?.conversation || 'مرحبا';
const customerName = data.data?.pushName || data.pushName || 'عميل';

return {
  json: {
    phone: phone,
    message: message,
    customerName: customerName,
    chatId: phone + '@s.whatsapp.net',
    intent: /حجز|رحلة|سفر/i.test(message) ? 'booking' : 'inquiry',
    timestamp: new Date().toISOString()
  }
};
```

---

## 🔍 للتشخيص:

إذا لسه مش شغال، أضف هذا الكود في **أول** Message Parser:

```javascript
// طباعة البيانات الواردة للتشخيص
const incoming = $input.first().json;
console.log('=== DEBUG ===');
console.log('Full Input:', JSON.stringify(incoming, null, 2));
console.log('=============');

// ثم باقي الكود...
```

ثم شوف الـ logs في n8n.

---

**جرب الكود المبسط (الثاني) واختبر!** 🚀

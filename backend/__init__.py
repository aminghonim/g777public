"""
Antigravity Backend - Core Modules
تعديل تقني: استخدام الـ Lazy Loading لتجنب أخطاء المكتبات المفقودة عند استدعاء جزء بسيط من النظام.
"""

# نترك ملف __init__.py فارغاً لتجنب الـ circular imports والـ ModuleNotFoundError الغير ضرورية
# سيتم استدعاء الموديولات مباشرة عند الحاجة (e.g. from backend.sender import WhatsAppSender)

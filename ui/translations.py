"""
نظام الترجمة - دعم العربية والإنجليزية
"""

from typing import Literal

TRANSLATIONS = {
    "ar": {
        # القائمة الجانبية
        "navigation": "التنقل",
        "group_sender": "مرسل المجموعات",
        "poll_sender": "مرسل الاستطلاعات",
        "members_grabber": "جالب الأعضاء",
        "links_grabber": "جالب الروابط",
        "google_maps": "خرائط جوجل",
        "social_media": "وسائل التواصل",
        "number_filter": "فلتر الأرقام",
        "account_warmer": "تسخين الحسابات",
        "cloud_hub": "مركز السحاب",
        "ai_assistant": "مساعد الذكاء",
        "whatsapp_pairing": "ربط الواتساب",
        "products_manager": "إدارة المنتجات",
        "business_setup": " إعداد النشاط",
        "crm_dashboard": "نظام العملاء",
        "opportunity_hunter": "صائد الفرص",
        "theme_settings": "المظهر",
        "poll_sender": "مرسل الاستطلاعات",
        "add_product": "إضافة منتج",
        "edit_product": "تعديل المنتج",
        "product_name": "اسم المنتج",
        "price": "السعر",
        "category": "القسم",
        "description": "الوصف",
        "available": "متاح",
        "stock": "المخزون",
        "auto_reply": "الرد التلقائي",
        "add_rule": "إضافة قاعدة",

        # Missing Keys (Audit Fix)
        "city_label": "المدينة:",
        "daily_messages_count": "عدد الرسائل اليومية",
        "delay_between_messages": "التأخير بين الرسائل (ثواني)",
        "engine_configuration": "إعدادات المحرك",
        "export_excel_button": "تصدير Excel",
        "grab_members_button": "سحب الأعضاء",
        "hunter_desc": "توليد عملاء محتملين بالذكاء الاصطناعي",
        "hunter_title": "صائد الفرص",
        "member_grabber_description": "استخراج بيانات أعضاء المجموعات بضغطة واحدة",
        "new_customer": "عميل جديد",
        "phone1_label": "رقم الحساب الأول",
        "phone2_label": "رقم الحساب الثاني",
        "products_catalog_desc": "إدارة المخزون والأسعار",
        "products_catalog_title": "مدير كتالوج المنتجات",
        "select_target_group": "اختر المجموعة المستهدفة",
        
        # الأزرار والعناوين
        "app_title": "G777",
        "app_subtitle": "ULTIMATE",
        "theme": "المظهر",
        "language": "اللغة",
        "settings": "الإعدادات",
        "refresh_btn": "تحديث",
        "full_reset_btn": "إعادة ضبط كاملة",
        
        # الرسائل والتنبيهات
        "welcome": "مرحباً بك",
        "theme_switched": "تم تغيير المظهر",
        "light_mode": "الوضع النهاري",
        "dark_mode": "الوضع الليلي",
        "deep_resetting": "جاري إعادة الضبط العميق...",
        "system_purged": "تم تنظيف النظام. احصل على كود جديد.",
        "enter_number_first": "أدخل الرقم أولاً",
        "generating_code": "جاري توليد الكود...",
        "code_generated": "الكود: ",
        "system_synchronized": "تم مزامنة النظام. البوت متصل الآن.",
        
        # الأزرار العامة
        "start": "بدء",
        "stop": "إيقاف",
        "clear": "مسح",
        "export": "تصدير",
        "import": "استيراد",
        "save": "حفظ",
        "cancel": "إلغاء",
        "confirm": "تأكيد",
        
        # الحالات
        "ready": "جاهز",
        "running": "قيد التشغيل",
        "stopped": "متوقف",
        "error": "خطأ",
        "success": "نجح",
        "error_loading": "خطأ في التحميل",
        "status_active": "نشط",
        "status_offline": "غير متصل",
        "awaiting_auth": "بانتظار المصادقة",
        "engine_status": "حالة المحرك",
        "live_badge": "مباشر",
        "initializing": "جاري تهيئة المحور...",
        
        # Group Sender Page
        "select_excel": "اختيار ملف إكسيل",
        "sheet": "الورقة",
        "message": "الرسالة",
        "start_local": "بدء إرسال محلي",
        "cloud_send": "إرسال سحابي بريميم",
        "data_preview": "معاينة البيانات",
        "no_file": "لم يتم اختيار ملف",
        "wait_sending": "جاري الإرسال...",
        "write_msg_hint": "اكتب رسالتك هنا... يمكنك استخدام {name} لوضع اسم العميل",
        "name_label": "الاسم",
        "phone_label": "الهاتف",
        "status_label": "الحالة",
        "contacts_count": "جهة اتصال",
        
        # Pairing Page
        "whatsapp_cloud_link": "ربط واتساب السحابي",
        "link_device_desc": "اربط جهازك بمحور الذكاء الاصطناعي",
        "link_via_code": "الربط عبر الكود",
        "phone_input_label": "رقم الهاتف",
        "scan_qr_title": "امسح رمز QR",
        "open_whatsapp_settings": "افتح إعدادات واتساب > الأجهزة المرتبطة",
        "link_established": "تم إنشاء الرابط",
        "connection_status": "حالة الاتصال",
        "checking_conn": "جاري فحص الاتصال...",
        "connected": "متصل ",
        "disconnected": "غير متصل ",
        "service_healthy": "الخدمة تعمل بشكل جيد",
        "service_issue": "تنبيه: يوجد مشكلة بالخدمة",
        "last_check": "آخر فحص",
        "scan_qr": "امسح الكود عبر واتساب",
        "force_refresh": "تحديث إجباري للحالة",
        "linked_with": "مرتبط بـ: ",
        "ai_sync": "مزامنة الذكاء",
        "enabled": "مفعل",
        "footer_api": "تكامل Evolution API v2.3.6",
        "footer_node": "عقدة الذكاء الاصطناعي: G777-Travel",

        # Business Setup & Theme (Final Fix)
        "business_setup_title": "إعداد ملف النشاط",
        "business_setup_desc": "تكوين شخصية مساعد الذكاء الاصطناعي",
        "messages_config_title": "رسائل الترحيب والوداع",
        "greeting_msg_label": "رسالة الترحيب",
        "greeting_msg_placeholder": "مرحباً! كيف يمكنني مساعدتك؟",
        "farewell_msg_label": "رسالة الوداع",
        "farewell_msg_placeholder": "شكراً لتواصلك معنا!",
        "off_hours_msg_label": "رسالة خارج أوقات العمل",
        "off_hours_msg_placeholder": "نحن خارج أوقات العمل حالياً...",
        "preview_label": "معاينة:",

        # Group Sender (Cyberpunk Theme)
        "data_matrix": "مصفوفة البيانات",
        "upload_excel": "رفع ملف Excel",
        "no_signal": "لا توجد إشارة",
        "select_sector": "اختر القطاع",
        "targets_acquired": "الأهداف المرصودة:",
        "payload_config": "إعداد الرسالة",
        "initiate_msg": "> ابدأ تسلسل الرسالة...",
        "group_invite_protocol": "> رابط دعوة المجموعة (URL)",
        "attach_visual": "إرفاق وسائط",
        "engine_core": "محرك النظام",
        "delay_flux": "التأخير الزمني (ثواني)",
        "active_cycle": "دورة النشاط (ساعات)",
        "engage": "تشغيل",
        "campaign_complete": "✅ اكتملت الحملة",
        "no_file_loaded": "لم يتم تحميل ملف",
        "no_visual_attached": "بانتظار إرفاق وسائط...",
        "attached_prefix": "تم إرفاق:",

        # Members & Links Grabber (Localization Fix)
        "member_grabber_title_large": "سحب الأعضاء",
        "member_grabber_subtitle": "استخراج بيانات أعضاء المجموعات بضغطة واحدة",
        "jid_label": "المعرف (JID)",
        "phone_column": "رقم الهاتف",
        "rank_column": "الرتبة",
        "search_placeholder": "بحث في النتائج...",
        
        "links_grabber_title_large": "صائد الروابط",
        "keywords_label": "كلمات البحث (Keyword)",
        "keywords_placeholder": "مثلاً: عقارات، استثمار، سيارات...",
        "target_count": "عدد المجموعات المستهدفة",
        "deep_hunt": "البحث العميق (Facebook)",
        "start_hunt": "ابدأ الصيد الآن",
        "links_found_title": "الروابط التي تم العثور عليها",
        "group_name_col": "اسم المجموعة",
        "link_col": "الرابط المكتشف",
        "status_col": "الحالة",

        # Maps & Social Extractor (Localization Fix)
        "maps_extractor_title": "مستخرج خرائط جوجل",
        "search_query_label": "بحث عن",
        "search_query_placeholder": "مثلا: مطاعم في القاهرة",
        "data_type_label": "نوع البيانات",
        "max_results_label": "أقصى عدد للنتائج",
        "extract_data_btn": "استخراج البيانات",
        "extracted_data_title": "البيانات المستخرجة",
        "business_name_col": "اسم النشاط",
        "address_col": "العنوان",
        
        "social_extractor_title": "مستخرج السوشيال ميديا",
        "platform_label": "المنصة",
        "url_label": "رابط الصفحة/الحساب",
        "url_placeholder": "https://...",
        "extract_contacts_btn": "استخراج جهات الاتصال",

        # Number Filter (Localization Fix)
        "number_filter_title_large": "فلترة الأرقام",
        "number_filter_subtitle": "فحص الأرقام وتصفية الحسابات النشطة على واتساب",
        "step_1_import": "1. استيراد الملف",
        "upload_excel_label": "اختر ملف Excel",
        "select_sheet_label": "اختر الورقة (Sheet)",
        "select_column_label": "اختر عمود الأرقام",
        "start_check_btn": "ابدأ الفحص",
        "total_numbers_label": "إجمالي الأرقام",
        "whatsapp_status_col": "الحالة على واتساب",
        
        # Automation Hub (Localization Fix)
        "automation_hub_title_large": "مركز الأتمتة",
        "automation_hub_subtitle": "مركز القيادة والتحكم للأتمتة الذكية",
        "connection_status_label": "حالة الاتصال",
        "ai_engine_label": "محرك الذكاء الاصطناعي",
        "active_campaigns_label": "الحملات النشطة",
        "quick_tip_title": "نصيحة سريعة:",
        "quick_tip_text": "يمكنك البدء بفلترة أرقامك أولاً عبر \"Number Filter\" ثم استخدام \"Group Sender\" لإطلاق حملتك الأولى.",
        "start_new_campaign_btn": "ابدأ حملة جديدة",
        "view_reports_btn": "عرض التقارير",

        # Account Warmer (Localization Fix)
        "account_warmer_title": "تسخين الحسابات",
        "account_warmer_subtitle": "تجهيز الحسابات الجديدة وتجنب الحظر عبر محاكاة الدردشة البشرية",
        "stop_warming_notify": "تم طلب إيقاف التسخين...",
        "start_warming_notify": "بدء عملية التسخين الذكية...",
        "warming_complete_notify": "اكتملت دورة التسخين.",
        "stop_warming_btn": "إيقاف التسخين",
        "start_warming_btn": "بدء التسخين",
        "logs_title": "سجلات النشاط",
        "warmer_ready_msg": "جاهز للبدء. اضغط على زر البدء...",
    },
    
    "en": {
        # Sidebar Navigation
        "navigation": "NAVIGATION",
        "group_sender": "GROUP SENDER",
        "poll_sender": "POLL SENDER",
        "members_grabber": "MEMBERS GRABBER",
        "links_grabber": "LINKS GRABBER",
        "google_maps": "GOOGLE MAPS",
        "social_media": "SOCIAL MEDIA",
        "number_filter": "NUMBER FILTER",
        "account_warmer": "ACCOUNT WARMER",
        "cloud_hub": "CLOUD HUB",
        "ai_assistant": "AI ASSISTANT",
        "whatsapp_pairing": "WHATSAPP PAIRING",
        "products_manager": "Products Manager",
        "business_setup": " Business Setup",
        "crm_dashboard": "CRM Dashboard",
        "opportunity_hunter": "Opportunity Hunter",
        "theme_settings": "Theme Settings",
        "poll_sender": "Poll Sender",
        "add_product": "Add Product",
        "edit_product": "Edit Product",
        "product_name": "Product Name",
        "price": "Price",
        "category": "Category",
        "description": "Description",
        "available": "Available",
        "stock": "Stock",
        
        # Buttons and Titles
        "app_title": "G777",
        "app_subtitle": "ULTIMATE",
        "theme": "Theme",
        "language": "Language",
        "settings": "Settings",
        "refresh_btn": "Refresh",
        "full_reset_btn": "Full Reset",
        
        # Messages
        "welcome": "Welcome",
        "theme_switched": "Theme Changed",
        "light_mode": "Light Mode",
        "dark_mode": "Dark Mode",
        "deep_resetting": "Deep Resetting...",
        "system_purged": "System Purged. Get new QR.",
        "enter_number_first": "Enter number first",
        "generating_code": "Generating code...",
        "code_generated": "CODE: ",
        "system_synchronized": "System Synchronized. Bot is now ONLINE.",
        
        # Common Buttons
        "start": "Start",
        "auto_reply": "Auto Reply",
        "add_rule": "Add Rule",

        # Missing Keys (Audit Fix)
        "city_label": "City:",
        "daily_messages_count": "Daily Messages Count",
        "delay_between_messages": "Delay Between Messages (sec)",
        "engine_configuration": "Engine Configuration",
        "export_excel_button": "Export Excel",
        "grab_members_button": "Grab Members",
        "hunter_desc": "AI-Powered Lead Generation",
        "hunter_title": "Opportunity Hunter",
        "member_grabber_description": "Extract group members in one click",
        "new_customer": "New Customer",
        "phone1_label": "First Account Number",
        "phone2_label": "Second Account Number",
        "products_catalog_desc": "Manage your inventory and pricing",
        "products_catalog_title": "Product Catalog Manager",
        "select_target_group": "Select Target Group",
        "stop": "Stop",
        "clear": "Clear",
        "export": "Export",
        "import": "Import",
        "save": "Save",
        "cancel": "Cancel",
        "confirm": "Confirm",
        
        # States
        "ready": "Ready",
        "running": "Running",
        "stopped": "Stopped",
        "error": "Error",
        "success": "Success",
        "error_loading": "Loading Error",
        "status_active": "ACTIVE",
        "status_offline": "OFFLINE",
        "awaiting_auth": "Awaiting user authentication",
        "engine_status": "Engine Status",
        "live_badge": "LIVE",
        "initializing": "Initializing hub...",

        # Group Sender Page
        "select_excel": "Select Excel",
        "sheet": "Sheet",
        "message": "Message",
        "start_local": "START LOCAL",
        "cloud_send": "CLOUD SEND (PREMIUM)",
        "data_preview": "Data Preview",
        "no_file": "No file selected",
        "wait_sending": "Sending...",
        "write_msg_hint": "Write your message here... use {name} for variable",
        "name_label": "Name",
        "phone_label": "Phone",
        "status_label": "Status",
        "contacts_count": "contacts",

        # Pairing Page
        "whatsapp_cloud_link": "WhatsApp Cloud Link",
        "link_device_desc": "Link your mobile device to the AI Intelligence Hub",
        "link_via_code": "Link via Code",
        "phone_input_label": "Phone Number",
        "scan_qr_title": "SCAN QR CODE",
        "open_whatsapp_settings": "Open WhatsApp Settings > Linked Devices",
        "link_established": "Link Established",
        "connection_status": "Connection Status",
        "checking_conn": "Checking connection...",
        "connected": "Connected ",
        "disconnected": "Disconnected ",
        "service_healthy": "Service Healthy",
        "service_issue": "Service Issue",
        "last_check": "Last check",
        "scan_qr": "Scan with WhatsApp",
        "force_refresh": "Force Refresh Status",
        "linked_with": "Linked: ",
        "ai_sync": "AI Sync",
        "enabled": "ENABLED",
        "footer_api": "Evolution API v2.3.6 Integration",
        "footer_node": "AI Intelligence Node: G777-Travel",

        # Business Setup & Theme (Final Fix)
        "business_setup_title": "Business Profile Setup",
        "business_setup_desc": "Configure your AI assistant's persona",
        "messages_config_title": "Greeting & Farewell Messages",
        "greeting_msg_label": "Greeting Message",
        "greeting_msg_placeholder": "Hello! How can I help you?",
        "farewell_msg_label": "Farewell Message",
        "farewell_msg_placeholder": "Thank you for contacting us!",
        "off_hours_msg_label": "Off-hours Message",
        "off_hours_msg_placeholder": "We are currently out of office...",
        "preview_label": "Preview:",

        # Group Sender (Cyberpunk Theme)
        "data_matrix": "DATA MATRIX",
        "upload_excel": "UPLOAD EXCEL",
        "no_signal": "NO SIGNAL SOURCE",
        "select_sector": "SELECT SECTOR",
        "targets_acquired": "TARGETS ACQUIRED:",
        "payload_config": "PAYLOAD CONFIG",
        "initiate_msg": "> INITIATE MESSAGE SEQUENCE...",
        "group_invite_protocol": "> GROUP INVITE PROTOCOL (URL)",
        "attach_visual": "ATTACH VISUAL ASSET",
        "engine_core": "ENGINE CORE",
        "delay_flux": "DELAY FLUX (SEC)",
        "active_cycle": "ACTIVE CYCLE (HRS)",
        "engage": "ENGAGE",
        "campaign_complete": "✅ CAMPAIGN SEQUENCE COMPLETE",
        "no_file_loaded": "NO FILE LOADED",
        "no_visual_attached": "AWAITING MEDIA...",
        "attached_prefix": "ATTACHED:",

        # Members & Links Grabber (Localization Fix)
        "member_grabber_title_large": "Members Grabber",
        "member_grabber_subtitle": "Extract group members in one click",
        "jid_label": "ID (JID)",
        "phone_column": "Phone Number",
        "rank_column": "Rank",
        "search_placeholder": "Search results...",
        
        "links_grabber_title_large": "Group Links Grabber",
        "keywords_label": "Keywords",
        "keywords_placeholder": "Ex: Real Estate, Crypto, Cars...",
        "target_count": "Target Count",
        "deep_hunt": "Deep Hunt (Facebook)",
        "start_hunt": "Start Hunt",
        "links_found_title": "Discovered Links",
        "group_name_col": "Group Name",
        "link_col": "Discovered Link",
        "status_col": "Status",

        # Maps & Social Extractor (Localization Fix)
        "maps_extractor_title": "Google Maps Extractor",
        "search_query_label": "Search Query",
        "search_query_placeholder": "e.g., Restaurants in Cairo",
        "data_type_label": "Data Type",
        "max_results_label": "Max Results",
        "extract_data_btn": "EXTRACT DATA",
        "extracted_data_title": "Extracted Data",
        "business_name_col": "Business Name",
        "address_col": "Address",
        
        "social_extractor_title": "Social Media Extractor",
        "platform_label": "Platform",
        "url_label": "Profile/Page URL",
        "url_placeholder": "https://...",
        "extract_contacts_btn": "EXTRACT CONTACTS",

        # Number Filter (Localization Fix)
        "number_filter_title_large": "Number Filter",
        "number_filter_subtitle": "Verify numbers and filter active WhatsApp accounts",
        "step_1_import": "1. Import File",
        "upload_excel_label": "Select Excel File",
        "select_sheet_label": "Select Sheet",
        "select_column_label": "Select Numbers Column",
        "start_check_btn": "Start Check",
        "total_numbers_label": "Total Numbers",
        "whatsapp_status_col": "WhatsApp Status",
        
        # Automation Hub (Localization Fix)
        "automation_hub_title_large": "Automation Hub",
        "automation_hub_subtitle": "Command & Control Center for Smart Automation",
        "connection_status_label": "Connection Status",
        "ai_engine_label": "AI Engine",
        "active_campaigns_label": "Active Campaigns",
        "quick_tip_title": "Quick Tip:",
        "quick_tip_text": "Start by filtering your numbers via 'Number Filter', then use 'Group Sender' to launch your first campaign.",
        "start_new_campaign_btn": "Start New Campaign",
        "view_reports_btn": "View Reports",

        # Account Warmer (Localization Fix)
        "account_warmer_title": "Account Warmer",
        "account_warmer_subtitle": "Prepare new accounts and avoid bans by simulating human chat",
        "stop_warming_notify": "Stopping warming process...",
        "start_warming_notify": "Starting smart warming...",
        "warming_complete_notify": "Warming cycle complete.",
        "stop_warming_btn": "STOP WARMING",
        "start_warming_btn": "START WARMING",
        "logs_title": "Activity Logs",
        "warmer_ready_msg": "Warmer ready. Press Start...",
    }
}

class LanguageManager:
    def __init__(self):
        self.current_lang: Literal["ar", "en"] = "ar"  # اللغة الافتراضية
    
    def set_language(self, lang: Literal["ar", "en"]):
        """تعيين اللغة"""
        if lang in ["ar", "en"]:
            self.current_lang = lang
    
    def toggle_language(self) -> str:
        """التبديل بين العربية والإنجليزية"""
        self.current_lang = "en" if self.current_lang == "ar" else "ar"
        return self.current_lang
    
    def get(self, key: str, default: str = "") -> str:
        """الحصول على الترجمة"""
        return TRANSLATIONS.get(self.current_lang, {}).get(key, default or key)
    
    def is_rtl(self) -> bool:
        """هل اللغة من اليمين لليسار؟"""
        return self.current_lang == "ar"
    
    def get_direction(self) -> str:
        """اتجاه النص"""
        return "rtl" if self.is_rtl() else "ltr"

# Instance عام
lang_manager = LanguageManager()

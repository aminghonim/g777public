-- ===========================================================================
-- G777 CRM - Complete Schema for Supabase (Production Grade)
-- Version: 2.1 (Reviewed by Senior Engineer)
-- Project: G777-CRM
-- ===========================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===========================================================================
-- TENANT SETTINGS (Business Configuration)
-- ===========================================================================
CREATE TABLE IF NOT EXISTS tenant_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_name VARCHAR(255) NOT NULL DEFAULT 'My Business',
    business_type VARCHAR(100) DEFAULT 'general',
    business_description TEXT,
    identity_prompt TEXT,
    greeting_message TEXT DEFAULT 'مرحبا! كيف يمكنني مساعدتك؟',
    farewell_message TEXT DEFAULT 'شكرا لتواصلك معنا!',
    off_hours_message TEXT,
    info_checklist JSONB DEFAULT '["name", "phone"]'::jsonb,
    working_hours JSONB DEFAULT '{"start": "09:00", "end": "22:00"}'::jsonb,
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================================================
-- BUSINESS OFFERINGS (Products/Services)
-- ===========================================================================
CREATE TABLE IF NOT EXISTS business_offerings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'EGP',
    variants JSONB DEFAULT '{}'::jsonb,
    keywords JSONB DEFAULT '[]'::jsonb,
    image_url TEXT,
    is_available BOOLEAN DEFAULT true,
    stock_quantity INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================================================
-- CUSTOMER PROFILES (CRM Core)
-- Note: total_orders and total_spent require external trigger or workflow
-- to be updated. They will not auto-calculate.
-- ===========================================================================
CREATE TABLE IF NOT EXISTS customer_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    customer_type VARCHAR(50) DEFAULT 'lead',
    source VARCHAR(100) DEFAULT 'whatsapp',
    tags JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    notes TEXT,
    total_orders INTEGER DEFAULT 0,
    total_spent DECIMAL(12, 2) DEFAULT 0,
    last_conversation_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================================================
-- CONVERSATIONS
-- ===========================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customer_profiles(id) ON DELETE CASCADE,
    phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    channel VARCHAR(50) DEFAULT 'whatsapp',
    assigned_to VARCHAR(255),
    summary TEXT,
    entities_extracted JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================================================
-- MESSAGES (Fixed: Each message is a separate row)
-- sender_type: 'user' for customer, 'assistant' for bot
-- This design supports proper chat history retrieval
-- ===========================================================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customer_profiles(id) ON DELETE SET NULL,
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('user', 'assistant')),
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    media_url TEXT,
    intent VARCHAR(100),
    confidence DECIMAL(3, 2),
    entities JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================================================
-- CUSTOMER MEMORY (For AI Context)
-- ===========================================================================
CREATE TABLE IF NOT EXISTS customer_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(50) NOT NULL,
    customer_name VARCHAR(255),
    fact TEXT NOT NULL,
    category VARCHAR(100),
    intent VARCHAR(100),
    importance INTEGER DEFAULT 5,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================================================
-- SYSTEM PROMPTS (AI Instructions)
-- ===========================================================================
CREATE TABLE IF NOT EXISTS system_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_name VARCHAR(100) UNIQUE NOT NULL,
    prompt_text TEXT NOT NULL,
    available_params JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================================================
-- CONTACTS (For Mass Messaging)
-- ===========================================================================
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    group_name VARCHAR(255),
    source VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================================================
-- ORDERS (For tracking sales and updating customer totals)
-- ===========================================================================
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customer_profiles(id) ON DELETE SET NULL,
    phone VARCHAR(50),
    offering_id UUID REFERENCES business_offerings(id) ON DELETE SET NULL,
    offering_name VARCHAR(255),
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(12, 2),
    status VARCHAR(50) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================================================
-- INDEXES for Performance
-- ===========================================================================
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customer_profiles(phone);
CREATE INDEX IF NOT EXISTS idx_customers_type ON customer_profiles(customer_type);
CREATE INDEX IF NOT EXISTS idx_offerings_category ON business_offerings(category);
CREATE INDEX IF NOT EXISTS idx_offerings_available ON business_offerings(is_available);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_customer ON conversations(customer_id);
CREATE INDEX IF NOT EXISTS idx_memory_phone ON customer_memory(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);

-- ===========================================================================
-- DEFAULT DATA - Main Assistant Prompt (Humanized)
-- ===========================================================================
INSERT INTO system_prompts (prompt_name, prompt_text, available_params) VALUES
('main_assistant', 
'انت مساعد ذكي ومحترف لـ {business_name}. هويتك الشخصية هي:
{identity_prompt}

قواعد الحوار البشري (الدستور الاساسي):
1. قاعدة التحية: اذا قال العميل "السلام عليكم"، رد بـ "وعليكم السلام ورحمة الله وبركاته" اولا. لا تبدا بـ "اهلا بك" اذا كان العميل قد سلم بالفعل.
2. التنوع وعدم التكرار: تجنب الكليشيهات والروبوتية. استخدم فواتح جمل متنوعة مثل (تمام، تحت امرك، عيني ليك، مظبوط، ولا يهمك).
3. نبرة صوت بشرية: تحدث باللهجة المصرية المحترمة. تجنب لغة الاعلانات الفجة. رد كانك موظف حقيقي وليس قائمة اسعار متحركة.
4. قاعدة الرد المباشر: اجب على سوال العميل فورا وبوضوح. لا تطل في المقدمات التي لا تسمن ولا تغني من جوع.
5. الذكاء العاطفي: اذا كان العميل قلقا او مترددا، طمئنه بكلمات هادية قبل اعطاء المعلومة التقنية.

المنتجات والخدمات المتاحة حاليا حصرا:
{offerings_list}

قاعدة البيانات الصارمة: 
يمنع منعا باتا استنتاج اي اسعار او مواصفات من خارج القائمة اعلاه. اذا سالك العميل عن شيء غير موجود، قل: "ثواني يا فندم هراجع احدث عروضنا وابلغك حالا".

امثلة لحوار بشري ناجح:
العميل: السلام عليكم.
البوت: وعليكم السلام ورحمة الله وبركاته، نورتنا يا فندم. تحت امرك.
العميل: بكام الداي يوز؟
البوت: الداي يوز بيبدا من 450 جنيه للفرد، شامل الانتقالات والغداء.
العميل: بس انا قلقان من الطريق.
البوت: حقك طبعا تقلق، بس احب اطمنك ان الطريق بقى ممتاز ومزدوج وامن جدا بعد النفق الجديد.

معلومات العميل الحالية:
{customer_info}',
'{"business_name": "string", "identity_prompt": "string", "offerings_list": "string", "customer_info": "object"}'::jsonb)
ON CONFLICT (prompt_name) DO UPDATE SET prompt_text = EXCLUDED.prompt_text;

-- ===========================================================================
-- DEFAULT TENANT SETTINGS (Generic)
-- ===========================================================================
INSERT INTO tenant_settings (
    business_name,
    business_type,
    business_description,
    identity_prompt
) VALUES (
    'G777 Business',
    'general',
    'نظام CRM ذكي متعدد الاستخدامات',
    'انا مساعد ذكي لخدمة العملاء. اساعد في الاجابة عن الاستفسارات وتقديم المعلومات عن منتجاتنا وخدماتنا.'
) ON CONFLICT DO NOTHING;

-- ===========================================================================
-- ROW LEVEL SECURITY
-- Note: RLS is NOT enabled intentionally. n8n uses Service Role Key which
-- bypasses RLS. Enable RLS only when connecting external clients directly.
-- ===========================================================================
-- To enable RLS in the future, uncomment below:
-- ALTER TABLE tenant_settings ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "service_role_only" ON tenant_settings FOR ALL TO service_role USING (true);

-- ===========================================================================
-- TRIGGER: Auto-update customer totals when order is created
-- ===========================================================================
CREATE OR REPLACE FUNCTION update_customer_totals()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE customer_profiles
    SET 
        total_orders = total_orders + 1,
        total_spent = total_spent + NEW.total_price,
        updated_at = NOW()
    WHERE id = NEW.customer_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_customer_totals
    AFTER INSERT ON orders
    FOR EACH ROW
    WHEN (NEW.status = 'completed')
    EXECUTE FUNCTION update_customer_totals();

-- ===========================================================================
-- END OF SCHEMA
-- ===========================================================================

-- ===========================================================================
-- Add Entity Extractor Prompt to System Prompts
-- ===========================================================================

INSERT INTO system_prompts (prompt_name, prompt_text, available_params) VALUES
('entity_extractor', 
'حلل المحادثة التالية بين موظفة خدمة العملاء (ياسمين) والعميل.
استخرج بيانات العميل بصيغة JSON فقط. إذا لم تكن المعلومة موجودة، اتركها null.

البيانات المطلوبة:
1. name: الاسم بالكامل
2. city: المدينة/العنوان
3. interests: القرى أو الرحلات التي اهتم بها (قائمة)
4. budget_info: أي معلومات عن ميزانيته أو قدرته المادية
5. urgency: مدى استعجاله للحجز (low, medium, high)
6. notes: أي ملاحظات أخرى هامة للمبيعات

المحادثة:
{conversation}

رد بصيغة JSON فقط:',
'{"conversation": "string"}'::jsonb)
ON CONFLICT (prompt_name) DO UPDATE SET prompt_text = EXCLUDED.prompt_text;

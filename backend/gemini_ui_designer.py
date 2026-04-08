"""
Antigravity UI Designer
يولد تصميمات UI كاملة من وصف نصي باستخدام Gemini 2.0 Flash
"""
import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

# إضافة مسار المشروع
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.ai_client import GeminiAIClient

logger = logging.getLogger(__name__)


class UIDesigner:
    """مصمم واجهات المستخدم بالذكاء الاصطناعي"""
    
    def __init__(self):
        self.ai_client = GeminiAIClient()
        self.designs_dir = project_root / "ui_designs"
        self.designs_dir.mkdir(exist_ok=True)
        
        # قوالب التصميم
        self.templates = {
            "web": "صفحة ويب حديثة",
            "mobile": "تطبيق موبايل",
            "dashboard": "لوحة تحكم",
            "landing": "صفحة هبوط"
        }
    
    def generate_ui_design(
        self,
        description: str,
        design_type: str = "web",
        style: str = "modern",
        color_scheme: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        توليد تصميم UI كامل من وصف نصي
        
        Args:
            description: وصف التصميم المطلوب
            design_type: نوع التصميم (web, mobile, dashboard, landing)
            style: الستايل (modern, minimal, dark, glassmorphism)
            color_scheme: نظام الألوان (اختياري)
        
        Returns:
            Dict يحتوي على HTML, CSS, وmetadata
        """
        
        # بناء الـ prompt المحترف
        prompt = self._build_design_prompt(description, design_type, style, color_scheme)
        
        # طلب Gemini لتوليد الكود
        try:
            response = self.ai_client.generate_response_sync(prompt)
            
            # استخراج الكود من الاستجابة
            html_code, css_code = self._extract_code(response)
            
            # حفظ التصميم
            design_id = self._save_design(
                description=description,
                html_code=html_code,
                css_code=css_code,
                design_type=design_type,
                style=style
            )
            
            return {
                "success": True,
                "design_id": design_id,
                "html": html_code,
                "css": css_code,
                "metadata": {
                    "description": description,
                    "type": design_type,
                    "style": style,
                    "created_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_design_prompt(
        self,
        description: str,
        design_type: str,
        style: str,
        color_scheme: Optional[str]
    ) -> str:
        """بناء prompt احترافي لـ Gemini"""
        
        style_guidelines = {
            "modern": """
                - استخدم تدرجات لونية حيوية (gradients)
                - تأثيرات hover ناعمة
                - خطوط Google Fonts (مثل Inter أو Poppins)
                - مسافات بيضاء كافية
            """,
            "minimal": """
                - ألوان محايدة (رمادي، أبيض، أسود)
                - بدون تأثيرات معقدة
                - خطوط بسيطة ونظيفة
                - تصميم نظيف وخفيف
            """,
            "dark": """
                - خلفية داكنة (#0a0e27 أو مشابه)
                - نصوص بيضاء أو رمادية فاتحة
                - تأثيرات ضوئية (glow effects)
                - contrasts عالية
            """,
            "glassmorphism": """
                - backdrop-filter: blur()
                - خلفيات شفافة
                - حدود ناعمة
                - تأثيرات زجاجية
            """
        }
        
        color_instruction = f"\n- نظام الألوان: {color_scheme}" if color_scheme else ""
        
        prompt = f"""
أنت مصمم UI/UX محترف. قم بتوليد كود HTML و CSS كامل لتصميم التالي:

**الوصف:** {description}
**النوع:** {design_type}
**الستايل:** {style}
{color_instruction}

**المتطلبات:**
{style_guidelines.get(style, style_guidelines["modern"])}

**الإرشادات:**
1. اكتب HTML كامل مع DOCTYPE
2. ضمّن CSS داخل <style> في الـ <head>
3. استخدم Semantic HTML5
4. اجعل التصميم Responsive
5. أضف Meta tags للـ SEO
6. لا تستخدم أي emojis داخل الكود
7. اجعل التصميم "WOW" - يجب أن يبهر المستخدم من أول نظرة

**ملاحظة مهمة:** 
- لا تضع الكود داخل ```html أو ```css
- أرجع الكود مباشرة بدون أي تنسيق markdown
- ابدأ مباشرة بـ <!DOCTYPE html>

الآن، قم بتوليد الكود الكامل:
"""
        
        return prompt.strip()
    
    def _extract_code(self, response: str) -> tuple[str, str]:
        """استخراج HTML و CSS من استجابة Gemini"""
        
        # إزالة markdown code blocks إذا وُجدت
        response = response.replace("```html", "").replace("```css", "").replace("```", "")
        
        # البحث عن HTML
        if "<!DOCTYPE html>" in response or "<html" in response:
            html_code = response
            
            # استخراج CSS من داخل <style>
            import re
            css_match = re.search(r'<style[^>]*>(.*?)</style>', html_code, re.DOTALL)
            css_code = css_match.group(1).strip() if css_match else ""
            
            return html_code, css_code
        else:
            # إذا لم يكن HTML كامل، اعتبره CSS
            return "", response
    
    def _save_design(
        self,
        description: str,
        html_code: str,
        css_code: str,
        design_type: str,
        style: str
    ) -> str:
        """حفظ التصميم في ملفات"""
        
        # توليد ID فريد
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        design_id = f"{design_type}_{timestamp}"
        
        # إنشاء مجلد التصميم
        design_folder = self.designs_dir / design_id
        design_folder.mkdir(exist_ok=True)
        
        # حفظ HTML
        html_file = design_folder / "index.html"
        html_file.write_text(html_code, encoding="utf-8")
        
        # حفظ CSS منفصل إذا كان موجود
        if css_code:
            css_file = design_folder / "style.css"
            css_file.write_text(css_code, encoding="utf-8")
        
        # حفظ metadata
        metadata = {
            "id": design_id,
            "description": description,
            "type": design_type,
            "style": style,
            "created_at": datetime.now().isoformat(),
            "files": {
                "html": str(html_file),
                "css": str(css_file) if css_code else None
            }
        }
        
        metadata_file = design_folder / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        
        logger.info(f"Design saved: {design_folder}")
        
        return design_id
    
    def list_designs(self) -> List[Dict[str, Any]]:
        """عرض قائمة التصميمات المحفوظة"""
        designs = []
        
        for design_folder in self.designs_dir.iterdir():
            if design_folder.is_dir():
                metadata_file = design_folder / "metadata.json"
                if metadata_file.exists():
                    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
                    designs.append(metadata)
        
        # ترتيب حسب التاريخ (الأحدث أولاً)
        designs.sort(key=lambda x: x["created_at"], reverse=True)
        
        return designs


# مثال على الاستخدام
if __name__ == "__main__":
    designer = UIDesigner()
    
    # اختبار توليد تصميم
    logger.info("🎨 Antigravity UI Designer")
    logger.info("=" * 50)
    
    description = input("اشرح وصف التصميم المطلوب: ").strip()
    if not description:
        description = "صفحة هبوط لتطبيق واتساب تسويقي، بتصميم عصري وألوان خضراء"
    
    logger.info(f"\n🚀 Generating design...")
    
    result = designer.generate_ui_design(
        description=description,
        design_type="landing",
        style="modern"
    )
    
    if result["success"]:
        logger.info(f"\n✅ Design generated successfully!")
        logger.info(f"   ID: {result['design_id']}")
        logger.info(f"   Location: {designer.designs_dir / result['design_id']}")
        logger.info(f"\n📂 Open index.html to view the design")
    else:
        logger.info(f"\n❌ Error: {result['error']}")

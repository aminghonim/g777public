"""اختبار سريع لـ Gemini UI Designer"""
import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.gemini_ui_designer import UIDesigner

designer = UIDesigner()

print("🎨 Testing Gemini UI Designer...")
print("=" * 60)

# توليد تصميم بسيط
result = designer.generate_ui_design(
    description="صفحة login بسيطة وعصرية بألوان زرقاء",
    design_type="web",
    style="modern"
)

if result["success"]:
    print(f"\n✅ SUCCESS!")
    print(f"   Design ID: {result['design_id']}")
    print(f"   Files saved in: ui_designs/{result['design_id']}/")
    print(f"\n📝 HTML Preview (first 500 chars):")
    print(result["html"][:500] + "...")
else:
    print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")

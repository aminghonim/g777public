import pytest
import os
from playwright.sync_api import Page, expect

# --- Configuration ---
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
if BASE_URL.endswith('/'):
    BASE_URL = BASE_URL[:-1]

def ensure_sidebar_visible(page: Page):
    """Ensure the sidebar is visible to access menu items."""
    # Check for a common menu item
    if not page.get_by_text("ربط الواتساب", exact=False).is_visible() and \
       not page.get_by_text("WHATSAPP PAIRING", exact=False).is_visible():
        menu_btn = page.locator("button:has-text('menu')").or_(page.locator(".q-btn:has(.q-icon:has-text('menu'))"))
        if menu_btn.is_visible():
            menu_btn.first.click()
            page.wait_for_timeout(500)

def navigate_to(page: Page, ar_name: str, en_name: str):
    """Helper to click sidebar menu item with retry logic"""
    ensure_sidebar_visible(page)
    try:
        # Increase timeout to 60 seconds (60000 ms) for slower environments
        page.get_by_text(ar_name, exact=False).or_(page.get_by_text(en_name, exact=False)).click(timeout=60000)
        page.wait_for_load_state("networkidle")
    except Exception as e:
        print(f"Navigation failed for {en_name}: {e}")
        raise e

# ==========================================
# EXTENDED FUNCTIONAL TESTS (Corrected)
# ==========================================

# NOTE: Product Management Page seems missing in ui/pages.py, skipping for now.

def test_tool_poll_sender(page: Page):
    """Verify Poll Sender Page"""
    page.goto(BASE_URL)
    navigate_to(page, "مرسل الاستطلاعات", "POLL SENDER")
    
    # Check for Poll Question Input using Label
    # Label: 'Poll Question'
    expect(page.get_by_text("Poll Question").or_(page.get_by_text("question"))).to_be_visible()
    # Check for Option textarea
    expect(page.locator("textarea")).to_be_visible()

def test_tool_member_grabber(page: Page):
    """Verify Group Members Grabber"""
    page.goto(BASE_URL)
    navigate_to(page, "جالب الأعضاء", "MEMBERS GRABBER")
    
    # Check for Input Label: 'Group Link or Name' or Placeholder
    expect(page.get_by_placeholder("https://chat.whatsapp.com/...", exact=False)).to_be_visible()
    # Check for Grab Button
    expect(page.locator("button").filter(has_text="GRAB MEMBERS")).to_be_visible()

def test_tool_link_grabber(page: Page):
    """Verify Group Links Grabber"""
    page.goto(BASE_URL)
    navigate_to(page, "جالب الروابط", "LINKS GRABBER")
    
    # Check for Search Input Placeholder
    expect(page.get_by_placeholder("e.g., Marketing, Business", exact=False)).to_be_visible()
    # Check for Start Button
    expect(page.locator("button").filter(has_text="START SEARCH")).to_be_visible()

def test_tool_google_maps(page: Page):
    """Verify Google Maps Extractor"""
    page.goto(BASE_URL)
    navigate_to(page, "خرائط جوجل", "GOOGLE MAPS")
    
    # Deep Check: Search Input Placeholder
    expect(page.get_by_placeholder("e.g., Restaurants in Cairo", exact=False)).to_be_visible()
    # Check for Extract Button
    expect(page.locator("button").filter(has_text="EXTRACT DATA")).to_be_visible()

def test_tool_social_media(page: Page):
    """Verify Social Media Extractor"""
    page.goto(BASE_URL)
    navigate_to(page, "وسائل التواصل", "SOCIAL MEDIA")
    
    # Check for Platform Selector Label
    expect(page.get_by_text("Platform")).to_be_visible()
    # Check for URL Input Placeholder
    expect(page.get_by_placeholder("https://...", exact=False)).to_be_visible()

def test_tool_number_filter(page: Page):
    """Verify Number Filter Tool"""
    page.goto(BASE_URL)
    navigate_to(page, "فلتر الأرقام", "NUMBER FILTER")
    
    # Check for Upload Area (usually contains specific text or is a file input)
    expect(page.locator("input[type='file']")).to_be_attached() 
    # Check for Filter Button (Exact text match to start to avoid duplicates)
    expect(page.get_by_text("FILTER NUMBERS", exact=False).first).to_be_visible()

def test_tool_account_warmer(page: Page):
    """Verify Account Warmer Tool"""
    page.goto(BASE_URL)
    navigate_to(page, "تسخين الحسابات", "ACCOUNT WARMER")
    
    # Check for Phone Inputs using Placeholder
    expect(page.get_by_placeholder("+20...", exact=False).first).to_be_visible()
    # Check for Delay Slider/Setting using text
    expect(page.get_by_text("Messages per Day").or_(page.get_by_text("رسالة في اليوم", exact=False))).to_be_visible()

def test_tool_ai_assistant(page: Page):
    """Verify AI Assistant Page"""
    page.goto(BASE_URL)
    navigate_to(page, "مساعد الذكاء", "AI ASSISTANT")
    
    # Check for Page Title
    expect(page.get_by_text("AI Marketing Assistant").or_(page.get_by_text("مساعد التسويق"))).to_be_visible()
    # Check for Input Placeholder
    expect(page.get_by_placeholder("Type your marketing strategy question...", exact=False)).to_be_visible()

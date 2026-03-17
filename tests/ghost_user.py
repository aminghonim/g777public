import asyncio
from playwright.async_api import async_playwright
import os

# Create screenshots directory
if not os.path.exists("tests/screenshots"):
    os.makedirs("tests/screenshots")

APP_URL = "http://127.0.0.1:8080"

async def run_ghost_user():
    async with async_playwright() as p:
        print("[Ghost] Launching Browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        try:
            print("[Ghost] Navigating to app...")
            await page.goto(APP_URL, timeout=60000, wait_until="commit")
            print("[Ghost] Page committed. Waiting for body...")
            await page.wait_for_selector("body", timeout=60000)
        except Exception as e:
            print(f"[Ghost] Error connecting: {e}")
            return

        # 1. Verify Initial State (Arabic)
        print("[Ghost] Checking Initial State (Arabic)...")
        await page.wait_for_timeout(2000) # Wait for hydration
        await page.screenshot(path="tests/screenshots/1_initial_state.png")
        
        # DEBUG: Save HTML to see what is happening
        content = await page.content()
        with open("tests/debug_initial.html", "w", encoding="utf-8") as f:
            f.write(content)
            
        # Check for Arabic text in Sidebar
        content = await page.content()
        if "إعداد النشاط" in content or "مرسل المجموعات" in content:
            print("✅ PASS: Arabic text detected.")
        else:
            print("❌ FAIL: Arabic text NOT detected.")

        # 2. Toggle Language to English
        print("[Ghost] Toggling Language to English...")
        # Find button with text "AR" or "EN" - assuming starts in AR
        # The button text depends on current_lang. If AR, button says "AR".
        try:
            # Click the language toggle button. Using exact=True to avoid matching "ENGAGE"
            await page.get_by_role("button", name="AR", exact=True).click()
            print("[Ghost] Language toggled. Waiting for reload...")
            await page.wait_for_timeout(5000) # Increased wait for reload
            await page.screenshot(path="tests/screenshots/2_english_state.png")
            
            content = await page.content()
            if "Business Setup" in content or "GROUP SENDER" in content:
                print("✅ PASS: Switched to English successfully.")
            else:
                print("❌ FAIL: English text NOT detected after toggle.")
                
        except Exception as e:
            print(f"⚠️ Warning during toggle: {e}")

        # 3. Navigate to Business Setup (English)
        print("[Ghost] Navigating to Business Setup...")
        try:
            # Note: The translation has a leading space " Business Setup"
            await page.get_by_text("Business Setup").click()
            # Wait for the header to appear to ensure page load
            try:
                # Wait for label specifically inside the form area or page content
                # "Greeting Message" is inside a label or textarea.
                print("[Ghost] Waiting for 'Greeting Message' text...")
                await page.wait_for_selector("text=Greeting Message", timeout=10000)
                print("[Ghost] Found 'Greeting Message'.")
            except Exception as e:
                print(f"[Ghost] 'Greeting Message' NOT FOUND: {e}")
                content = await page.content()
                print(f"[Ghost] Business Setup Page Content Snippet: {content[:500]}...") # Print first 500 chars

            await page.screenshot(path="tests/screenshots/3_business_setup.png")
            
            # Check for Form Labels
            content = await page.content()
            if "Greeting Message" in content:
                 print("✅ PASS: Business Setup Page loaded.")
            else:
                 print("❌ FAIL: Business Setup Page missing 'Greeting Message'.")
        except Exception as e:
             print(f"⚠️ Navigation Error: {e}")

        # 4. Navigate to Group Sender (Top Tab) - still in English
        print("[Ghost] Navigating to Group Sender...")
        try:
            await page.get_by_text("GROUP SENDER").first.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path="tests/screenshots/4_group_sender.png")
            
            if "DATA MATRIX" in await page.content():
                print("✅ PASS: Group Sender loaded correctly (Cyberpunk Theme Check).")
            else:
                print("❌ FAIL: Group Sender missing 'DATA MATRIX'.")
        except Exception as e:
             print(f"⚠️ Navigation Error: {e}")

        # 5. Switch back to Arabic to test Group Sender localization
        print("[Ghost] Switching back to Arabic...")
        try:
             # Look for "EN" button. 
             # Note: If previous step failed, we might still be in English anyway.
             await page.get_by_role("button", name="EN", exact=True).click()
             print("[Ghost] Toggled back to Arabic. Waiting for reload...")
             await page.wait_for_timeout(5000)
             
             # RELOAD RESETS TO DEFAULT PAGE. WE MUST NAVIGATE BACK TO GROUP SENDER.
             # In Arabic, "Group Sender" is "مرسل المجموعات"
             print("[Ghost] Navigating back to Group Sender (in Arabic)...")
             try:
                await page.get_by_text("مرسل المجموعات").click()
                await page.wait_for_timeout(2000)
             except:
                print("[Ghost] Could not find 'مرسل المجموعات' link. Trying generic wait.")

             await page.screenshot(path="tests/screenshots/5_arabic_group_sender.png")
             
             content = await page.content()
             if "مصفوفة البيانات" in content or "المرسل الجماعي" in content:
                 print("✅ PASS: Group Sender localized to Arabic.")
             else:
                 print("❌ FAIL: Group Sender Arabic localization failed.")
        except Exception as e:
             print(f"⚠️ Toggle Error: {e}")

        print("[Ghost] Simulation Complete.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_ghost_user())

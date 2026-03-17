
import os
import time
from backend.browser_core import WhatsAppBrowser

def open_youtube_for_login():
    print("=" * 60)
    print("[Interactive] Opening YouTube for Login...")
    print("[Interactive] Please log in to your Premium account in the opened browser.")
    print("[Interactive] ONCE LOGGED IN: Press ENTER here in the terminal to save session and continue.")
    print("=" * 60)
    
    # Initialize browser with persistent profile
    browser = WhatsAppBrowser(headless=False)
    driver = browser.initialize_driver()
    
    try:
        # Go to YouTube
        driver.get("https://www.youtube.com")
        
        # Wait for user to signal completion
        input("\n>>> Press ENTER after you have successfully logged in to YouTube...")
        
        print("[Interactive] Login captured. Closing browser to save profile...")
        
    except Exception as e:
        print(f"[Error] {e}")
    finally:
        browser.close()
        print("[Interactive] Session saved in chrome_profile.")

if __name__ == "__main__":
    open_youtube_for_login()

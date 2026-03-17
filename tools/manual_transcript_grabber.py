
import os
import time
from backend.browser_core import WhatsAppBrowser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_youtube_transcript(video_url, output_file="transcript.txt"):
    print(f"[Automation] Starting browser to grab transcript from: {video_url}")
    
    # We use the existing WhatsAppBrowser core but for YouTube
    browser = WhatsAppBrowser(headless=False)
    driver = browser.initialize_driver()
    
    try:
        driver.get(video_url)
        time.sleep(5)  # Let it load
        
        # Click "More" in description to find transcript button if needed
        # Or try to find the transcript button directly
        print("[Automation] Looking for transcript...")
        
        # YouTube's transcript is usually hidden in the "..." menu
        try:
            # Click the "More" button in description
            expand_desc = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-button[@id='expand']"))
            )
            expand_desc.click()
            time.sleep(2)
        except:
            print("[Automation] Could not find expand button, trying direct transcript find...")

        # Try alternative: Search for any content that looks like a description
        print("[Automation] Attempting to grab full page text for analysis...")
        try:
            full_text = driver.find_element(By.TAG_NAME, "body").text
            with open("raw_page_text.txt", "w", encoding="utf-8") as f:
                f.write(full_text)
            print("[Automation] Saved raw page text to raw_page_text.txt")
        except:
            print("[Automation] Failed to save raw text.")

    except Exception as e:
        print(f"[Automation] Critical Error: {e}")
        driver.save_screenshot("d:/WORK/2/debug_youtube_error.png")
    finally:
        browser.close()

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=8xsFYYv_jnw"
    get_youtube_transcript(url)

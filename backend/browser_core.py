import time
import logging
from typing import Optional, List
from .core.i18n import t

# Configure logging
logger = logging.getLogger(__name__)

class WhatsAppBrowser:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.logger = logging.getLogger(__name__)

    def initialize_driver(self):
        """Initialize the undetected chrome driver."""
        try:
            import undetected_chromedriver as uc
            options = uc.ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            self.driver = uc.Chrome(options=options)
            self.logger.info(t("browser.logs.started", "Browser core initialized."))
            return self.driver
        except Exception as e:
            self.logger.error(f"Failed to init browser: {e}")
            raise

    def scan_qr(self):
        """Wait for user to scan QR."""
        if not self.driver:
            self.initialize_driver()
        
        self.driver.get("https://web.whatsapp.com")
        self.logger.info(t("browser.logs.waiting_qr", "Waiting for QR Scan..."))
        
        # Poll for login
        max_wait = 60
        start = time.time()
        while time.time() - start < max_wait:
            try:
                # Check for search box which appears after login
                self.driver.find_element("css selector", "div[contenteditable='true']")
                self.logger.info(t("browser.logs.login_success", "Logged into WhatsApp Web successfully!"))
                return True
            except:
                time.sleep(2)
        
        self.logger.warning(t("browser.logs.timeout", "QR Scan Timeout."))
        return False

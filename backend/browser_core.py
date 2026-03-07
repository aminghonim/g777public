"""
Browser Core Module
Handles Chrome browser initialization using undetected-chromedriver.
Maintains persistent WhatsApp login sessions.
"""

import os
import time
import subprocess
from pathlib import Path
from .core.i18n import t

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


class WhatsAppBrowser:
    """
    WhatsApp Web browser controller using undetected-chromedriver.

    Features:
    - Undetectable Chrome instance (bypasses WhatsApp detection)
    - Persistent login session (scan QR once, stay logged forever)
    - Stable on Windows with proper flags
    - Explicit wait for login completion
    """

    WHATSAPP_URL = "https://web.whatsapp.com"
    CHAT_LIST_SELECTOR = "#pane-side"  # Element visible after successful login

    def __init__(self, headless: bool = False):
        """
        Initialize WhatsAppBrowser configuration.

        Args:
            headless (bool): Run browser without visible window (default: False)
                            Note: Headless mode may trigger detection, use with caution
        """
        self.headless = headless
        self.driver = None

        # Set up persistent profile directory in project root
        self.project_root = Path(__file__).parent.parent
        self.profile_path = self.project_root / "chrome_profile"

        # Create profile directory if it doesn't exist
        self.profile_path.mkdir(parents=True, exist_ok=True)

        print(
            t("browser.logs.profile_dir", "[Browser] Profile directory: {path}").format(
                path=self.profile_path
            )
        )

    def force_kill_chrome(self):
        """Kill any zombie Chrome processes to free the profile."""
        try:
            # print("[Browser] Cleaning up stale Chrome processes...")
            subprocess.run(
                "taskkill /F /IM chrome.exe /T",
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                "taskkill /F /IM chromedriver.exe /T",
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )
            time.sleep(1)  # Wait for file locks to release
        except Exception:
            pass

    def initialize_driver(self) -> uc.Chrome:
        """
        Initialize and launch undetected Chrome browser.
        """
        # Return existing driver if already running
        if self.driver:
            try:
                self.driver.current_url
                print(
                    t(
                        "browser.logs.driver_initialized",
                        "[Browser] Driver already initialized.",
                    )
                )
                return self.driver
            except:
                self.driver = None

        print(t("browser.logs.initializing", "[Browser] Initializing Chrome driver..."))
        self.force_kill_chrome()  # FORCE CLEANUP
        self.force_kill_chrome()  # Ensure clean slate significantly reduces conflicts

        # Configure Chrome options
        options = uc.ChromeOptions()

        # Persistent session - user data directory
        options.add_argument(f"--user-data-dir={self.profile_path}")

        # Stability flags for Windows
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")

        # Performance optimizations
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Window size for consistent rendering
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")

        # Headless mode (if enabled)
        if self.headless:
            options.add_argument("--headless=new")

        try:
            # Initialize undetected Chrome with automatic version detection
            # Initialize undetected Chrome with explicit version to avoid beta conflicts
            self.driver = uc.Chrome(
                options=options,
                use_subprocess=True,
                version_main=144,  # Fixed version to match installed Chrome
            )

            # Set implicit wait
            self.driver.implicitly_wait(10)

            print(
                t(
                    "browser.logs.success_init",
                    "[Browser] Success: Chrome driver initialized successfully",
                )
            )
            return self.driver

        except Exception as e:
            print(
                t(
                    "browser.logs.error_init",
                    "[Browser] Error: Failed to initialize driver: {err}",
                ).format(err=e)
            )

            # Retry with explicit version detection
            try:
                print(
                    t(
                        "browser.logs.retrying",
                        "[Browser] Retrying with version detection...",
                    )
                )

                # Try to get Chrome version on Windows
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                ]

                version_main = None
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        result = subprocess.run(
                            [chrome_path, "--version"], capture_output=True, text=True
                        )
                        version_str = result.stdout.strip()
                        # Extract major version (e.g., "Google Chrome 120.0.6099.130" -> 120)
                        version_main = int(version_str.split()[2].split(".")[0])
                        print(
                            t(
                                "browser.logs.detected_version",
                                "[Browser] Detected Chrome version: {ver}",
                            ).format(ver=version_main)
                        )
                        break

                # Re-create options to avoid "cannot reuse ChromeOptions" error
                retry_options = uc.ChromeOptions()
                retry_options.add_argument(f"--user-data-dir={self.profile_path}")
                retry_options.add_argument("--no-sandbox")
                retry_options.add_argument("--disable-gpu")
                retry_options.add_argument("--disable-dev-shm-usage")
                retry_options.add_argument("--disable-extensions")
                retry_options.add_argument("--disable-popup-blocking")
                retry_options.add_argument(
                    "--disable-blink-features=AutomationControlled"
                )
                retry_options.add_argument("--window-size=1920,1080")
                retry_options.add_argument("--start-maximized")
                if self.headless:
                    retry_options.add_argument("--headless=new")

                self.driver = uc.Chrome(
                    options=retry_options,
                    use_subprocess=True,
                    version_main=144,  # Fixed version
                )

                self.driver.implicitly_wait(10)
                print(
                    t(
                        "browser.logs.success_retry",
                        "[Browser] Success: Chrome driver initialized (with version override)",
                    )
                )
                return self.driver

            except Exception as retry_error:
                print(
                    t(
                        "browser.logs.error_retry",
                        "[Browser] Error: Retry failed: {err}",
                    ).format(err=retry_error)
                )
                raise WebDriverException(f"Failed to initialize Chrome: {retry_error}")

    def wait_for_login(self, timeout: int = 120) -> bool:
        """
        Wait for WhatsApp login to complete.

        This method waits for the chat list pane (#pane-side) to become visible,
        which indicates successful login (either via QR scan or cached session).

        Args:
            timeout (int): Maximum seconds to wait for login (default: 120)

        Returns:
            bool: True if login successful, False if timeout
        """
        print(
            t(
                "browser.logs.waiting_login",
                "[Browser] Waiting for login (timeout: {sec}s)...",
            ).format(sec=timeout)
        )
        print(
            t(
                "browser.logs.qr_tip",
                "[Browser] If this is your first time, please scan the QR code.",
            )
        )

        try:
            wait = WebDriverWait(self.driver, timeout)

            # Wait for chat list to be visible (indicates successful login)
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.CHAT_LIST_SELECTOR)
                )
            )

            print(
                t(
                    "browser.logs.success_login",
                    "[Browser] Success: Login successful! WhatsApp is ready.",
                )
            )
            return True

        except TimeoutException:
            print(
                t(
                    "browser.logs.timeout_login",
                    "[Browser] Error: Login timeout after {sec} seconds",
                ).format(sec=timeout)
            )
            return False

    def load_whatsapp(self, login_timeout: int = 120) -> bool:
        """
        Navigate to WhatsApp Web and wait for login.

        This is the main method to get WhatsApp ready for automation.

        Args:
            login_timeout (int): Maximum seconds to wait for login (default: 120)

        Returns:
            bool: True if WhatsApp loaded and logged in successfully

        Raises:
            WebDriverException: If driver not initialized
        """
        if not self.driver:
            raise WebDriverException(
                "Driver not initialized. Call initialize_driver() first."
            )

        print(
            t("browser.logs.navigating", "[Browser] Navigating to {url}").format(
                url=self.WHATSAPP_URL
            )
        )

        try:
            self.driver.get(self.WHATSAPP_URL)

            # Small delay for page to start loading
            time.sleep(2)

            # Wait for login
            return self.wait_for_login(timeout=login_timeout)

        except Exception as e:
            print(
                t(
                    "browser.logs.error_init",
                    "[Browser] Error: Failed to load WhatsApp: {err}",
                ).format(err=e)
            )
            return False

    def is_logged_in(self) -> bool:
        """
        Check if currently logged into WhatsApp.

        Returns:
            bool: True if logged in, False otherwise
        """
        if not self.driver:
            return False

        try:
            self.driver.find_element(By.CSS_SELECTOR, self.CHAT_LIST_SELECTOR)
            return True
        except:
            return False

    def refresh(self) -> bool:
        """
        Refresh WhatsApp Web page.

        Returns:
            bool: True if refresh successful and still logged in
        """
        if not self.driver:
            return False

        try:
            print(t("browser.logs.refreshing", "[Browser] Refreshing page..."))
            self.driver.refresh()
            time.sleep(3)
            return self.wait_for_login(timeout=30)
        except Exception as e:
            print(f"[Browser] Error: Refresh failed: {e}")
            return False

    def take_screenshot(self, filename: str = "screenshot.png") -> str:
        """
        Take a screenshot of the current page.

        Args:
            filename (str): Name for the screenshot file

        Returns:
            str: Path to the saved screenshot
        """
        if not self.driver:
            return ""

        screenshot_dir = self.project_root / "data" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        filepath = screenshot_dir / filename
        self.driver.save_screenshot(str(filepath))
        print(
            t(
                "browser.logs.screenshot_saved", "[Browser] Screenshot saved: {path}"
            ).format(path=filepath)
        )
        return str(filepath)

    def close(self) -> None:
        """
        Safely close the browser and clean up resources.
        """
        if self.driver:
            try:
                print(t("browser.logs.closing", "[Browser] Closing browser..."))
                self.driver.quit()
                self.driver = None
                print(
                    t(
                        "browser.logs.closed_success",
                        "[Browser] Success: Browser closed successfully",
                    )
                )
            except Exception as e:
                print(f"[Browser] Warning during close: {e}")
                self.driver = None

    def __enter__(self):
        """Context manager entry - initialize driver."""
        self.initialize_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close browser."""
        self.close()
        return False


# Standalone test
if __name__ == "__main__":
    print("=" * 60)
    print("WhatsApp Browser Core - Test")
    print("=" * 60)

    # Using context manager for automatic cleanup
    with WhatsAppBrowser(headless=False) as browser:
        if browser.load_whatsapp(login_timeout=120):
            print("\nSuccess: WhatsApp is ready for automation!")
            print("Press Enter to close the browser...")
            input()
        else:
            print("\nError: Failed to load WhatsApp")

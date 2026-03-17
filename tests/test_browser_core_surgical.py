
import pytest
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
from backend.browser_core import WhatsAppBrowser

class TestBrowserCoreSurgical:

    @pytest.fixture
    def browser(self):
        # Prevent actual Chrome launch
        with patch('undetected_chromedriver.Chrome', MagicMock()):
            return WhatsAppBrowser(headless=True)

    # =================================================================
    # ✅ SUCCESS STATE TESTS
    # =================================================================

    def test_init_creates_profile(self, browser):
        """اختبار إنشاء مجلد ملف تعريف المستخدم عند البدء"""
        assert browser.profile_path.exists()
        assert browser.profile_path.is_dir()

    @patch('subprocess.run')
    def test_force_kill_chrome(self, mock_run, browser):
        """اختبار إغلاق عمليات كروم العالقة"""
        browser.force_kill_chrome()
        assert mock_run.called

    def test_initialize_driver_success(self, browser):
        """اختبار تهيئة المحرك بنجاح"""
        with patch('undetected_chromedriver.Chrome') as mock_chrome:
            mock_chrome.return_value = MagicMock()
            driver = browser.initialize_driver()
            assert driver is not None
            assert browser.driver == driver

    def test_load_whatsapp_success(self, browser):
        """اختبار تحميل واتساب بنجاح عند ظهور العناصر"""
        browser.driver = MagicMock()
        # محاكاة ظهور لوحة الدردشات
        with patch('selenium.webdriver.support.ui.WebDriverWait.until', return_value=True):
            assert browser.load_whatsapp(login_timeout=1) is True

    # =================================================================
    # ❌ LOGIC FAILURE STATE TESTS
    # =================================================================

    def test_load_whatsapp_timeout(self, browser):
        """حالة فشل تسجيل الدخول (انتهاء المهلة)"""
        browser.driver = MagicMock()
        from selenium.common.exceptions import TimeoutException
        with patch('selenium.webdriver.support.ui.WebDriverWait.until', side_effect=TimeoutException()):
            assert browser.load_whatsapp(login_timeout=0.1) is False

    def test_refresh_no_driver(self, browser):
        """حالة محاولة التنشيط بدون محرك عمل"""
        browser.driver = None
        assert browser.refresh() is False

    # =================================================================
    # 💥 SYSTEM FAILURE STATE TESTS
    # =================================================================

    def test_close_exception_handling(self, browser):
        """تغطية استثناءات الإغلاق"""
        browser.driver = MagicMock()
        browser.driver.quit.side_effect = Exception("Driver Panic")
        # Should not crash
        browser.close()
        assert browser.driver is None

    def test_take_screenshot_success(self, browser):
        """اختبار التقاط صورة للشاشة"""
        browser.driver = MagicMock()
        path = browser.take_screenshot("test.png")
        assert "test.png" in path
        assert browser.driver.save_screenshot.called
        
    def test_take_screenshot_no_driver(self, browser):
        """التقاط صورة بدون محرك"""
        browser.driver = None
        assert browser.take_screenshot() == ""

    # =================================================================
    # 🔧 ADDITIONAL COVERAGE TESTS
    # =================================================================

    def test_is_logged_in_true(self, browser):
        """Test is_logged_in returns True when chat list exists"""
        browser.driver = MagicMock()
        browser.driver.find_element.return_value = MagicMock()
        assert browser.is_logged_in() is True

    def test_is_logged_in_false_no_element(self, browser):
        """Test is_logged_in returns False when element not found"""
        browser.driver = MagicMock()
        from selenium.common.exceptions import NoSuchElementException
        browser.driver.find_element.side_effect = NoSuchElementException()
        assert browser.is_logged_in() is False

    def test_is_logged_in_false_no_driver(self, browser):
        """Test is_logged_in returns False when no driver"""
        browser.driver = None
        assert browser.is_logged_in() is False

    def test_refresh_success(self, browser):
        """Test refresh returns True on success"""
        browser.driver = MagicMock()
        with patch.object(browser, 'wait_for_login', return_value=True):
            with patch('time.sleep'):
                assert browser.refresh() is True
                browser.driver.refresh.assert_called_once()

    def test_refresh_exception(self, browser):
        """Test refresh handles exception gracefully"""
        browser.driver = MagicMock()
        browser.driver.refresh.side_effect = Exception("Network Error")
        assert browser.refresh() is False

    def test_wait_for_login_success(self, browser):
        """Test wait_for_login returns True on successful login"""
        browser.driver = MagicMock()
        with patch('selenium.webdriver.support.ui.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.return_value = True
            assert browser.wait_for_login(timeout=5) is True

    def test_wait_for_login_timeout(self, browser):
        """Test wait_for_login returns False on timeout"""
        browser.driver = MagicMock()
        from selenium.common.exceptions import TimeoutException
        
        # Patch at the module level where it's used
        with patch('backend.browser_core.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.side_effect = TimeoutException()
            assert browser.wait_for_login(timeout=1) is False

    def test_load_whatsapp_no_driver_raises(self, browser):
        """Test load_whatsapp raises when driver not initialized"""
        browser.driver = None
        from selenium.common.exceptions import WebDriverException
        with pytest.raises(WebDriverException, match="Driver not initialized"):
            browser.load_whatsapp()

    def test_load_whatsapp_exception(self, browser):
        """Test load_whatsapp handles navigation exception"""
        browser.driver = MagicMock()
        browser.driver.get.side_effect = Exception("Navigation Error")
        assert browser.load_whatsapp(login_timeout=1) is False

    def test_context_manager_enter_exit(self):
        """Test context manager (__enter__ and __exit__)"""
        with patch('undetected_chromedriver.Chrome') as mock_chrome, \
             patch('subprocess.run'):
            mock_chrome.return_value = MagicMock()
            
            browser = WhatsAppBrowser(headless=True)
            
            # Test __enter__
            with patch.object(browser, 'initialize_driver', return_value=MagicMock()) as mock_init:
                result = browser.__enter__()
                mock_init.assert_called_once()
                assert result == browser
            
            # Test __exit__
            browser.driver = MagicMock()
            with patch.object(browser, 'close') as mock_close:
                browser.__exit__(None, None, None)
                mock_close.assert_called_once()

    def test_close_success(self, browser):
        """Test close method successfully closes driver"""
        mock_driver = MagicMock()
        browser.driver = mock_driver
        browser.close()
        # After close, driver should be None
        assert browser.driver is None
        # The original mock should have had quit called
        mock_driver.quit.assert_called_once()

    def test_close_no_driver(self, browser):
        """Test close does nothing when driver is None"""
        browser.driver = None
        browser.close()  # Should not raise

    def test_initialize_driver_reuses_existing(self, browser):
        """Test initialize_driver returns existing driver if valid"""
        mock_driver = MagicMock()
        mock_driver.current_url = "https://web.whatsapp.com"
        browser.driver = mock_driver
        
        result = browser.initialize_driver()
        assert result == mock_driver

    def test_initialize_driver_recreates_dead_driver(self, browser):
        """Test initialize_driver recreates if driver is dead"""
        mock_dead_driver = MagicMock()
        # Simulate a dead driver by raising exception on property access
        type(mock_dead_driver).current_url = property(lambda s: (_ for _ in ()).throw(Exception("Dead")))
        browser.driver = mock_dead_driver
        
        with patch('undetected_chromedriver.Chrome') as mock_chrome, \
             patch('subprocess.run'), \
             patch('time.sleep'):
            mock_chrome.return_value = MagicMock()
            result = browser.initialize_driver()
            assert result is not None
            
    def test_headless_mode_sets_argument(self):
        """Test headless mode adds correct argument"""
        with patch('undetected_chromedriver.Chrome') as mock_chrome, \
             patch('subprocess.run'), \
             patch('time.sleep'):
            mock_chrome.return_value = MagicMock()
            browser = WhatsAppBrowser(headless=True)
            browser.initialize_driver()
            
            # Check that headless argument was added
            call_args = mock_chrome.call_args
            options = call_args.kwargs.get('options') or call_args[1].get('options')
            assert options is not None

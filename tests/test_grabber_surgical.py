
import pytest
from unittest.mock import MagicMock, patch, mock_open, call, PropertyMock
import sys
import os
import io

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.grabber import DataGrabber

class TestGrabberSurgical:
    """
    Surgical Coverage Test for backend/grabber.py
    Target: 100% Coverage by mocking Selenium & Pandas
    """

    @pytest.fixture
    def mock_driver(self):
        """Mock Selenium Driver (undetected-chromedriver)"""
        driver = MagicMock()
        # Fix: browser_core imports `undetected_chromedriver as uc`, not `webdriver`
        with patch('backend.browser_core.uc.Chrome', return_value=driver):
             yield driver

    @pytest.fixture
    def grabber(self, mock_driver):
        """Return DataGrabber instance with mocked driver"""
        # Patch init to avoid real browser launch if possible, 
        # but since we inherit from WhatsAppBrowser which calls init, we rely on the implementation.
        # Ideally we just instantiate and the mocked Chrome fixture handles the underlying call.
        gb = DataGrabber(headless=True)
        gb.driver = mock_driver # Ensure fixture driver is used
        return gb

    def test_init(self, mock_driver):
        """Test Initialization"""
        gb = DataGrabber()
        assert gb.headless is False
        
    def test_get_group_name(self, grabber, mock_driver):
        """Test _get_group_name strategies"""
        # Strategy 1: Sidebar Title
        el1 = MagicMock()
        el1.get_attribute.return_value = "Group A"
        mock_driver.find_elements.side_effect = [[el1], [], []]
        name = grabber._get_group_name()
        assert name == "Group A"
        
        # Strategy 2: Header Fallback
        mock_driver.find_elements.side_effect = [[], [], []] # Fail all sidebar
        mock_driver.find_element.return_value.text = "Header Group"
        name = grabber._get_group_name()
        assert name == "Header Group"
        
        # Strategy 3: Unknown
        mock_driver.find_element.side_effect = Exception("No Header")
        name = grabber._get_group_name()
        assert name == "Unknown_Group"

    def test_scrape_interactive_mode_flow(self, grabber, mock_driver):
        """Test main scraping flow with branches"""
        # 1. Driver not init
        grabber.driver = None
        with patch.object(DataGrabber, 'initialize_driver'):
            with patch.object(DataGrabber, 'load_whatsapp', return_value=False):
                res = grabber.scrape_interactive_mode()
                assert res == (None, "WhatsApp load failed")

        # 2. Dialog missing (Timeout)
        grabber.driver = mock_driver
        with patch.object(DataGrabber, '_get_group_name', return_value="G1"):
             with patch('backend.grabber.WebDriverWait') as mock_wait:
                 mock_wait.return_value.until.side_effect = Exception("Timeout") # Simulate Timeout via Exception match for simplicty or specific TimeoutException
                 # Note: Code catches TimeoutException from selenium.common.exceptions
                 # We must raise the correct type or mock the import
                 from selenium.common.exceptions import TimeoutException
                 mock_wait.return_value.until.side_effect = TimeoutException()
                 
                 res = grabber.scrape_interactive_mode()
                 assert "Dialog not found" in res[1]

        # 3. Success via Primary Strategy
        grabber.driver = mock_driver
        with patch.object(DataGrabber, '_get_group_name', return_value="G1"):
             with patch('backend.grabber.WebDriverWait'): # Dialog check pass
                 with patch.object(DataGrabber, '_enhanced_extraction_strategy', return_value=("file.xlsx", "Done")):
                     res = grabber.scrape_interactive_mode()
                     assert res[0] == "file.xlsx"

        # 4. Fallback Strategy Trigger
        with patch.object(DataGrabber, '_get_group_name', return_value="G1"):
             with patch('backend.grabber.WebDriverWait'):
                 with patch.object(DataGrabber, '_enhanced_extraction_strategy', return_value=(None, "Fail")):
                     with patch.object(DataGrabber, '_fallback_selenium_extraction', return_value=("fallback.xlsx", "Done")):
                         res = grabber.scrape_interactive_mode()
                         assert res[0] == "fallback.xlsx"

    def test_enhanced_strategy_logic(self, grabber, mock_driver):
        """Test _enhanced_extraction_strategy logic (JS Injection)"""
        # Simulate JS returning mock members logic
        
        # 1. Successful loop
        mock_driver.execute_script.side_effect = [
            # Batch 1
            [{"phone": "123", "name": "Ali", "index": 0}, {"phone": "456", "name": "Bob", "index": 1}],
            # Batch 2 (No new) to trigger stop
            [{"phone": "123", "name": "Ali", "index": 0}, {"phone": "456", "name": "Bob", "index": 1}],
             # ... repeats ...
        ] 
        # Since we loop max_no_new times (8), we need enough side_effects or loose mock
        mock_driver.execute_script.return_value = [{"phone": "111", "name": "A", "index": 0}] # Always return same, triggers no new data
        
        with patch.object(DataGrabber, '_save_members', return_value=("f.xlsx", "ok")):
             with patch.object(DataGrabber, '_smart_scroll', return_value=True):
                 res = grabber._enhanced_extraction_strategy("G1")
                 assert res[0] == "f.xlsx"
                 
        # 2. JS Crash
        mock_driver.execute_script.side_effect = Exception("JS Crash")
        res = grabber._enhanced_extraction_strategy("G1")
        assert res[0] is None # Returns None, "No members found..."

    def test_smart_scroll(self, grabber, mock_driver):
        """Test _smart_scroll"""
        # Success
        mock_driver.execute_script.return_value = True
        assert grabber._smart_scroll() is True
        
        # Exception
        mock_driver.execute_script.side_effect = Exception("Scroll err")
        assert grabber._smart_scroll() is False

    def test_fallback_selenium(self, grabber, mock_driver):
        """Test _fallback_selenium_extraction"""
        # 1. Found Items
        element = MagicMock()
        element.text = "User +1234567890" 
        mock_driver.find_elements.side_effect = [[element], [], [], []]
        
        with patch.object(DataGrabber, '_save_members', return_value=("f.xlsx", "ok")):
            res = grabber._fallback_selenium_extraction("G1")
            assert res[0] == "f.xlsx"

        # 2. No Items
        mock_driver.find_elements.side_effect = None # FIX: Clear exhausted side_effect
        mock_driver.find_elements.return_value = []
        res = grabber._fallback_selenium_extraction("G1")
        assert "No elements" in res[1]

    def test_grabber_edge_cases(self, grabber, mock_driver):
        """Cover remaining edge cases and exceptions"""
        
        # 1. Scrape Interactive Exception (Lines 72-76)
        with patch.object(DataGrabber, '_get_group_name', side_effect=Exception("CritFail")):
             res = grabber.scrape_interactive_mode()
             assert "CritFail" in res[1]

        # 2. Group Name Filters (Lines 367-381)
        el_click = MagicMock()
        el_click.get_attribute.return_value = "Click here for info" # Ignored
        el_list = MagicMock()
        el_list.get_attribute.return_value = "A, B, C, D, E" # Ignored (Too many commas)
        el_time = MagicMock()
        el_time.get_attribute.return_value = "12:00" # Ignored (Time)
        
        mock_driver.find_elements.return_value = [el_click, el_list, el_time]
        mock_driver.find_element.side_effect = Exception("No Header") # Fallback fail
        
        name = grabber._get_group_name()
        assert name == "Unknown_Group"

        # 3. Save Members Exception (Lines 459-461)
        with patch('backend.grabber.pd') as mock_pd:
             mock_pd.DataFrame.side_effect = Exception("PD Fail")
             with pytest.raises(Exception):
                 grabber._save_members({}, "method")

        # 4. Group Joiner Exception (Lines 498-502)
        grabber.driver = mock_driver
        with patch('backend.grabber.WebDriverWait', side_effect=Exception("Wait Fail")):
             grabber.group_joiner(["link"]) # Should catch and print
        
        # 5. Number Filter Driver Init (Lines 511-513)
        grabber.driver = None
        with patch.object(DataGrabber, 'load_whatsapp', return_value=False):
             assert grabber.number_filter(["1"]) == []

        # 6. Number Filter Timeout (Lines 538-542)
        grabber.driver = mock_driver
        mock_driver.find_elements.side_effect = lambda by, val: [] # Never find
        from selenium.common.exceptions import TimeoutException
        with patch('backend.grabber.WebDriverWait') as mock_wait:
             mock_wait.return_value.until.side_effect = TimeoutException()
             res = grabber.number_filter(["123"])
             assert res == []

    def test_loop_exceptions(self, grabber, mock_driver):
        """Cover exception handlers inside loops which are swallowed"""
        # Line 322: Exception inside item loop in fallback
        element_crash = MagicMock()
        # Accessing .text raises exception
        type(element_crash).text = PropertyMock(side_effect=Exception("Item access fail"))
        mock_driver.find_elements.return_value = [element_crash]
        
        # Should continue and return "No valid phone numbers" (Line 326)
        res = grabber._fallback_selenium_extraction("G1")
        assert "No valid phone numbers" in res[1]

        # Line 305: text is empty
        element_empty = MagicMock()
        element_empty.text = "" 
        mock_driver.find_elements.return_value = [element_empty]
        res = grabber._fallback_selenium_extraction("G1")
        assert "No valid phone numbers" in res[1]
        
        # Line 507: Number filter exceptions check
        grabber.driver = mock_driver
        # First number raises Exception, Second works
        mock_driver.get.side_effect = [Exception("Nav Fail"), None] 
        
        # Smart Mock for find_elements:
        # 1. First number fails due to get(), so find_elements not called (or logic skips)
        # 2. Second number succeeds. WebDriverWait checks #main or invalid text.
        # We return ["ok"] for #main to simulate valid number.
        def smart_side_effect(by, value):
            if value == "#main": return ["Element"]
            return []
            
        mock_driver.find_elements.side_effect = smart_side_effect
        
        with patch('backend.grabber.WebDriverWait'): # Pass wait
             res = grabber.number_filter(["111", "222"])
             assert "222" in res
             assert "111" not in res

    def test_save_members(self, grabber):
        """Test Excel saving logic using Pandas Mock"""
        members = {"123": {"name": "A", "phone": "123"}}
        
        # Mock Pandas
        with patch('backend.grabber.pd') as mock_pd:
            with patch('os.path.exists', return_value=False): # New file
                mock_df = MagicMock()
                mock_pd.DataFrame.return_value = mock_df
                
                path, msg = grabber._save_members(members, "method", "Group1")
                assert "Created new" in msg
                mock_df.to_excel.assert_called()

            # Append mode
            with patch('os.path.exists', return_value=True):
                 # Successful append
                 with patch('backend.grabber.pd.ExcelWriter') as mock_writer:
                      path, msg = grabber._save_members(members, "method", "Group1")
                      assert "Updated existing" in msg
                      
                 # Locked file -> Backup
                 with patch('backend.grabber.pd.ExcelWriter', side_effect=Exception("Locked")):
                      path, msg = grabber._save_members(members, "method", "Group1")
                      assert "locked/error" in msg

    def test_group_joiner(self, grabber, mock_driver):
        """Test group joiner logic"""
        # Not processed driver
        grabber.driver = None
        with patch.object(DataGrabber, 'load_whatsapp', return_value=False):
             assert grabber.group_joiner(["link"]) == []
        
        # Success Join
        grabber.driver = mock_driver
        with patch('backend.grabber.WebDriverWait') as mock_wait:
             btn = MagicMock()
             mock_wait.return_value.until.return_value = btn
             joined = grabber.group_joiner(["link1"])
             assert "link1" in joined
             btn.click.assert_called()
             
        # Timeout Join
        mock_driver.reset_mock()
        from selenium.common.exceptions import TimeoutException
        with patch('backend.grabber.WebDriverWait') as mock_wait:
             mock_wait.return_value.until.side_effect = TimeoutException()
             joined = grabber.group_joiner(["link2"])
             assert joined == []

    def test_number_filter(self, grabber, mock_driver):
        """Test number filter logic"""
        # Setup
        grabber.driver = mock_driver
        
        # Valid Number
        # Mock driver.find_elements to return non-empty for "#main"
        mock_driver.find_elements.side_effect = lambda by, val: ["valid"] if "#main" in val else []
        
        # Since find_elements checks multiple things in lambda wait, 
        # we mock WebDriverWait simply
        with patch('backend.grabber.WebDriverWait'):
             res = grabber.number_filter(["123"])
             assert "123" in res

        # Invalid Number
        # Mock find_elements to return empty for main, but found for invalid text
        mock_driver.find_elements.side_effect = lambda by, val: ["fail"] if "invalid" in val else []
        with patch('backend.grabber.WebDriverWait'):
             res = grabber.number_filter(["456"])
             assert "456" not in res # Should detect invalid

    def test_create_poll_stub(self, grabber):
        """Test create_poll stub"""
        assert grabber.create_poll("Q", []) is None

    def test_grabber_gap_fillers(self, grabber, mock_driver):
        """Fill the final 5% coverage gaps"""

        # 1. _get_group_name internal exception (Lines 399-401)
        # We need to trigger the outer except block. Exceptions inside the loop are caught.
        # We can mock 'print' to raise an exception at the very beginning (Line 341).
        # We use a list side_effect so the second print (in exception handler) succeeds.
        with patch('builtins.print', side_effect=[Exception("Outer Crash"), None, None]):
            name = grabber._get_group_name()
            assert name == "Unknown_Group"

        # 2. _get_group_name gridcell fallback (Lines 362-363)
        mock_driver.find_elements.side_effect = None # Reset
        el_grid = MagicMock()
        el_grid.find_element.side_effect = Exception("No Title Span")
        el_grid.text = "Fallback Name\nDetails"
        
        # We need matching selector to return [el_grid]
        def selector_side_effect(by, selector):
            if "gridcell" in selector: return [el_grid]
            return []
        mock_driver.find_elements.side_effect = selector_side_effect
        
        name = grabber._get_group_name()
        assert name == "Fallback Name"

        # 3. _get_group_name empty title attribute (Line 367)
        el_no_title = MagicMock()
        el_no_title.get_attribute.return_value = ""
        el_no_title.text = "Text Name"
        
        # Reset side effect first
        mock_driver.find_elements.side_effect = None
        
        def selector_side_effect_2(by, selector):
            # Return match if it's NOT gridcell AND contains title
            if "gridcell" not in selector and "span[title]" in selector and "pane-side" not in selector:
                 return [el_no_title]
            return []
        mock_driver.find_elements.side_effect = selector_side_effect_2
        name = grabber._get_group_name()
        assert name == "Text Name"

        # 4. _save_members empty sheet name fallback (Line 429)
        # Using a name that sanitizes to empty string
        members = {"1": {"name": "n", "phone": "1", "index": 0}}
        with patch('backend.grabber.pd') as mock_pd:
            with patch('os.makedirs'):
                 grabber._save_members(members, "test", group_name=":::////")
                 mock_pd.DataFrame.assert_called()

        # 5. group_joiner fatal loop error (Lines 501-502)
        grabber.driver = mock_driver
        # First link fails fundamentally, second succeeds
        mock_driver.get.side_effect = [Exception("Fatal Get"), None] 
        # For second link, let's just say button not found to exit fast
        with patch('backend.grabber.WebDriverWait', side_effect=Exception("No Button")):
             grabber.group_joiner(["link1", "link2"])
        
        # 6. _fallback_selenium_extraction outer exception (Lines 330-333)
        mock_driver.find_elements.side_effect = Exception("Outer Crash")
        res = grabber._fallback_selenium_extraction("G1")
        assert "Fallback error" in res[1]


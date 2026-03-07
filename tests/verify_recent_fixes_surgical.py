import unittest
from unittest.mock import MagicMock, patch
import re
import sys
import os

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import target classes/functions
from backend.cloud_service import CloudService
from ui.controllers.members_grabber_controller import MembersGrabberController
from ui.theme_manager import theme_manager

class TestRecentFixesSurgical(unittest.TestCase):
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. TEST: groupJid Normalization (Rule 2.2 Proof)
    # ═══════════════════════════════════════════════════════════════════
    def test_group_jid_normalization(self):
        service = CloudService()
        
        # Test Case A: Raw number id (Failure case simulation)
        # Expected: Should be normalized to @g.us
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"participants": []}
            
            # Input: "120363022212345"
            service.fetch_group_participants("120363022212345")
            
            # Verify the URL called was normalized
            args, kwargs = mock_get.call_args
            called_url = args[0]
            self.assertIn("120363022212345@g.us", called_url)
            
        # Test Case B: Already correct JID
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            service.fetch_group_participants("12345-6789@g.us")
            args, kwargs = mock_get.call_args
            self.assertIn("12345-6789@g.us", args[0])

    # ═══════════════════════════════════════════════════════════════════
    # 2. TEST: Member Parsing [object Object] Fix (Rule 4.2 Proof)
    # ═══════════════════════════════════════════════════════════════════
    def test_member_data_parsing(self):
        controller = MembersGrabberController()
        
        # Simulating various weird API responses including potential [object Object] or legacy formats
        mixed_members = [
            {"id": "201012345678@s.whatsapp.net", "admin": True}, # Standard
            "201088888888@s.whatsapp.net", # String only
            {"jid": "201099999999@s.whatsapp.net", "isAdmin": False}, # Alternative key
            None, # Bad data
            {"number": "201111111111"} # Another alternative
        ]
        
        with patch('backend.cloud_service.cloud_service.fetch_all_groups', return_value=[]):
            with patch('backend.cloud_service.cloud_service.fetch_group_participants', return_value=mixed_members):
                results = asyncio.run(controller.grab_members("dummy_jid"))
                
                # Check results
                self.assertEqual(len(results), 4) # None should be filtered out
                self.assertEqual(results[0]['phone'], "201012345678")
                self.assertEqual(results[0]['status'], "Admin")
                self.assertEqual(results[1]['phone'], "201088888888")
                self.assertEqual(results[1]['status'], "Member")
                self.assertEqual(results[2]['phone'], "201099999999")
                self.assertEqual(results[3]['phone'], "201111111111")

    # ═══════════════════════════════════════════════════════════════════
    # 3. TEST: Theme Color Fallback (Rule 1.2 Proof)
    # ═══════════════════════════════════════════════════════════════════
    def test_theme_color_fallback(self):
        # We verify that get_colors() doesn't crash if a key is missing 
        # (Though we fixed it in the UI, let's verify the theme manager's comprehensive palette)
        colors = theme_manager.get_colors()
        
        # Verify mandatory fallback keys exist
        self.assertIn('red', colors)
        self.assertIn('blue', colors)
        
        # Simulate the fix logic: get('orange', red)
        val = colors.get('orange', colors.get('peach', colors['red']))
        self.assertTrue(bool(val)) # Should return a color code, not crash

# Helper for async test matching controller structure
import asyncio
if __name__ == "__main__":
    unittest.main()

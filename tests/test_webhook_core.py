"""
Webhook Core Tests - SYNC-ONLY for stability
Tests basic webhook handler flows without async conflicts.

Updated to match extract_message_info v2 signature:
  Returns: (text, jid, from_me, media_type, media_metadata) - 5 values
"""

import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.message_processor import extract_message_info


class TestWebhookCore:
    """Synchronous webhook tests focusing on individual components"""

    def test_extract_message_info_valid(self):
        """Test message extraction from valid payload"""
        payload = {
            "data": {
                "key": {"remoteJid": "201000000000@s.whatsapp.net", "fromMe": False},
                "message": {"conversation": "Hello Bot"}
            }
        }

        text, jid, from_me, media_type, media_metadata = extract_message_info(payload)

        assert text == "Hello Bot"
        assert jid == "201000000000@s.whatsapp.net"
        assert from_me is False
        assert media_type is None
        assert media_metadata is None

    def test_extract_message_info_from_me(self):
        """Test that fromMe flag is correctly extracted"""
        payload = {
            "data": {
                "key": {"remoteJid": "201000000000@s.whatsapp.net", "fromMe": True},
                "message": {"conversation": "My message"}
            }
        }

        text, jid, from_me, _media_type, _media_metadata = extract_message_info(payload)

        assert from_me is True

    def test_extract_message_info_empty(self):
        """Test extraction from empty payload"""
        payload = {}

        text, jid, from_me, _media_type, _media_metadata = extract_message_info(payload)

        assert text is None or text == ""
        assert jid is None or jid == ""

    def test_extract_extended_text(self):
        """Test extraction of extended text message"""
        payload = {
            "data": {
                "key": {"remoteJid": "201000000000@s.whatsapp.net", "fromMe": False},
                "message": {"extendedTextMessage": {"text": "Extended Hello"}}
            }
        }

        text, jid, from_me, _media_type, _media_metadata = extract_message_info(payload)

        assert text == "Extended Hello"

    def test_extract_from_legacy_format(self):
        """Test extraction from legacy payload format (no data wrapper)"""
        payload = {
            "key": {"remoteJid": "201111111111@s.whatsapp.net", "fromMe": False},
            "message": {"conversation": "Legacy format"}
        }

        text, jid, from_me, _media_type, _media_metadata = extract_message_info(payload)

        # The function should handle both formats
        assert text is not None or jid is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.agents.skills.intent_alignment import IntentAlignment


def test_vague_create_intent():
    ia = IntentAlignment()
    # Mocking or assuming config exists
    # If the real config is loaded, "create app" should be a trigger.
    # We should probably mock _load_config for isolation, but this is an integration test.

    triggers = [{"keyword": "create app", "threshold": 0.8, "questions": 3}]
    ia.config = {"triggers": triggers}

    result = ia.analyze_intent("I want to create app for managing inventory")
    assert result["needs_brainstorming"] is True
    assert result["questions_count"] == 3


def test_specifc_fix_intent():
    ia = IntentAlignment()
    triggers = [{"keyword": "create app", "threshold": 0.8, "questions": 3}]
    ia.config = {"triggers": triggers}

    result = ia.analyze_intent("fix bug in header")
    assert result["needs_brainstorming"] is False

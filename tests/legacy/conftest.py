"""
Frontend Test Fixtures - Shared test utilities
"""

import pytest
from pathlib import Path


@pytest.fixture
def theme_config_path():
    """Path to theme configuration"""
    return Path(__file__).parent.parent.parent / "ui" / "ui_theme_master.json"


@pytest.fixture
def mock_theme_config():
    """Mock theme configuration for testing"""
    return {
        "name": "Test Theme",
        "version": "1.0.0",
        "available_themes": [
            {
                "id": "test_dark",
                "name": "Test Dark",
                "type": "dark",
                "palette": ["#050a12", "#00e5ff", "#ff8c00"],
                "semantic": {
                    "primary": "#00e5ff",
                    "secondary": "#0a1628",
                    "accent": "#ff8c00",
                    "bg_app": "#050a12",
                    "bg_card": "#0a1628",
                    "border": "#1a3a5c",
                    "border_glow_cyan": "#00e5ff",
                    "border_glow_orange": "#ff8c00",
                    "border_glow_purple": "#b040ff",
                    "text_main": "#e0f7ff",
                    "text_muted": "#8cb4d4"
                }
            }
        ]
    }


@pytest.fixture
def app_url():
    """Base URL for E2E tests"""
    return "http://localhost:8080"

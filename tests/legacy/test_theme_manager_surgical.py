import pytest
from unittest.mock import MagicMock, patch, mock_open
import json
import sys
import os

# Ensure backend/ui path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock nicegui BEFORE import
sys.modules["nicegui"] = MagicMock()

from ui.theme_manager import ThemeManager

class TestThemeManagerSurgical:
    """
    Surgical tests for ui/theme_manager.py
    """

    @patch("builtins.open", new_callable=mock_open, read_data='{"available_themes": [{"id": "t1", "name": "Theme 1", "semantic": {"primary": "#000"}}]}')
    @patch("pathlib.Path.exists")
    def test_init_load(self, mock_exists, mock_file):
        """Test initialization loads themes."""
        mock_exists.return_value = False # No settings file
        
        manager = ThemeManager()
        
        assert len(manager.get_available_themes()) == 1
        assert manager.current_theme_id == "huemint1_light" # Default fallback
        assert manager.is_dark() is False

    @patch("builtins.open", new_callable=mock_open, read_data='{"theme_id": "test_theme", "dark_mode": true}')
    @patch("json.load")
    @patch("pathlib.Path.exists")
    def test_init_with_settings(self, mock_exists, mock_json_load, mock_file):
        """Test initialization with existing settings."""
        mock_exists.return_value = True
        # Mock json.load to return separate dicts for theme config and settings
        mock_json_load.side_effect = [
            {"available_themes": []}, # Theme config
            {"theme_id": "test_theme", "dark_mode": True} # Settings
        ]
        
        manager = ThemeManager()
        
        assert manager.current_theme_id == "test_theme"
        assert manager.is_dark() is True
        assert manager.current_mode == "dark"

    def test_get_current_theme_fallback(self):
        """Test fallback when current theme ID not found."""
        manager = ThemeManager()
        manager.themes = {"available_themes": [{"id": "t1"}, {"id": "t2"}]}
        manager.current_theme_id = "non_existent"
        
        theme = manager.get_current_theme()
        assert theme["id"] == "t1" # First available

    @patch("ui.theme_manager.ui")
    def test_set_theme(self, mock_ui):
        """Test setting theme updates state and calls UI colors."""
        manager = ThemeManager()
        manager.themes = {"available_themes": [{"id": "t1", "semantic": {"primary": "#123"}}]}
        manager._save_settings = MagicMock()
        
        manager.set_theme("t1")
        
        assert manager.current_theme_id == "t1"
        mock_ui.colors.assert_called_once()
        manager._save_settings.assert_called_once()

    @patch("ui.theme_manager.ui")
    def test_set_dark_mode(self, mock_ui):
        """Test toggling dark mode."""
        manager = ThemeManager()
        manager._save_settings = MagicMock()
        
        manager.set_dark_mode(True)
        
        assert manager.is_dark() is True
        assert manager.current_mode == "dark"
        # Verify ui.dark_mode().value set
        assert mock_ui.dark_mode.return_value.value is True
        manager._save_settings.assert_called_once()

    def test_get_colors_structure(self):
        """Test get_colors returns expected merged structure."""
        manager = ThemeManager()
        manager.get_current_theme = MagicMock(return_value={
            "semantic": {"primary": "#ABC", "bg_app": "#FFF"}
        })
        
        colors = manager.get_colors()
        
        assert colors["primary"] == "#ABC"
        assert colors["background"] == "#FFF" # mapped
        assert "rosewater" in colors # default catppuccin
        
    def test_get_quasar_classes(self):
        """Test CSS class mapping."""
        manager = ThemeManager()
        css = manager.get_quasar_classes("bg-primary")
        assert "var(--cat-primary)" in css
        
        fallback = manager.get_quasar_classes("unknown")
        assert "var(--cat-primary)" in fallback

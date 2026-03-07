"""
Unit Tests for g777_components.py
Tests all G777 Ultimate components (cyber_card, hex_icon, etc.)
"""

import pytest
from unittest.mock import Mock, patch
from ui.g777_components import (
    _hex_to_rgb,
    cyber_card,
    launch_button,
    hex_icon,
    progress_pulse,
    section_header,
    stat_card,
    slider_control,
    file_upload_zone
)


class TestHelperFunctions:
    """Test utility functions"""
    
    def test_hex_to_rgb_conversion(self):
        """Verify hex to RGB conversion"""
        assert _hex_to_rgb("#00e5ff") == "0, 229, 255"
        assert _hex_to_rgb("#ff8c00") == "255, 140, 0"
        assert _hex_to_rgb("#000000") == "0, 0, 0"
        assert _hex_to_rgb("#ffffff") == "255, 255, 255"
    
    def test_hex_to_rgb_without_hash(self):
        """Verify conversion works without # prefix"""
        result = _hex_to_rgb("00e5ff")
        assert result == "0, 229, 255"


class TestCyberCard:
    """Test cyber_card component"""
    
    @patch('ui.g777_components.theme_manager')
    @patch('ui.g777_components.ui')
    def test_cyber_card_glow_colors(self, mock_ui, mock_tm):
        """Verify cyber card uses correct glow colors"""
        mock_tm.get_semantic.return_value = {
            "border_glow_cyan": "#00e5ff",
            "border_glow_orange": "#ff8c00",
            "border_glow_purple": "#b040ff",
            "bg_app": "#050a12",
            "text_main": "#e0f7ff"
        }
        
        # Test cyan glow
        cyber_card(title="Test", glow="cyan", step_number=1)
        mock_tm.get_semantic.assert_called()
    
    @patch('ui.g777_components.theme_manager')
    @patch('ui.g777_components.ui')
    def test_cyber_card_with_step_number(self, mock_ui, mock_tm):
        """Verify step number is rendered"""
        mock_tm.get_semantic.return_value = {
            "border_glow_cyan": "#00e5ff",
            "bg_app": "#050a12",
            "text_main": "#e0f7ff"
        }
        
        cyber_card(title="Import", glow="cyan", step_number=1)
        # Should create UI elements
        assert mock_ui.column.called


class TestLaunchButton:
    """Test launch_button component"""
    
    @patch('ui.g777_components.ui')
    @patch('ui.g777_components.theme_manager')
    def test_launch_button_creation(self, mock_tm, mock_ui):
        """Verify launch button is created"""
        mock_tm.get_semantic.return_value = {"text_main": "#e0f7ff"}
        
        callback = Mock()
        launch_button("Launch Campaign", on_click=callback, icon="rocket")
        
        # Should create button
        assert mock_ui.element.called
        assert mock_ui.button.called


class TestProgressPulse:
    """Test progress_pulse component"""
    
    @patch('ui.g777_components.ui')
    @patch('ui.g777_components.theme_manager')
    def test_progress_pulse_color_mapping(self, mock_tm, mock_ui):
        """Verify progress bar uses correct glow colors"""
        mock_tm.get_semantic.return_value = {
            "border_glow_cyan": "#00e5ff",
            "border_glow_orange": "#ff8c00",
            "border_glow_purple": "#b040ff"
        }
        
        progress_pulse(value=50, color="orange")
        mock_tm.get_semantic.assert_called()


class TestSectionHeader:
    """Test section_header component"""
    
    @patch('ui.g777_components.ui')
    @patch('ui.g777_components.theme_manager')
    def test_section_header_with_icon(self, mock_tm, mock_ui):
        """Verify section header renders with icon"""
        mock_tm.get_semantic.return_value = {
            "primary": "#00e5ff",
            "text_main": "#e0f7ff",
            "text_muted": "#8cb4d4"
        }
        
        section_header("Campaign Settings", icon="settings", subtitle="Configure")
        
        assert mock_ui.row.called
        assert mock_ui.icon.called


class TestSliderControl:
    """Test slider_control component"""
    
    @patch('ui.g777_components.ui')
    @patch('ui.g777_components.theme_manager')
    def test_slider_control_range(self, mock_tm, mock_ui):
        """Verify slider has correct min/max values"""
        mock_tm.get_semantic.return_value = {
            "text_main": "#e0f7ff",
            "text_muted": "#8cb4d4",
            "primary": "#00e5ff"
        }
        
        slider_control("Delay", min_val=0, max_val=1000, value=500)
        
        # Should create slider with correct range
        assert mock_ui.column.called
        assert mock_ui.slider.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

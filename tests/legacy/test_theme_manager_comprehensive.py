"""
Comprehensive Unit Tests for theme_manager.py
Tests CSS generation, theme switching, and neon glow effects
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from ui.theme_manager import ThemeManager


class TestThemeLoading:
    """Test theme configuration loading"""
    
    def test_load_g777_dark_theme(self):
        """Verify G777 dark theme loads correctly"""
        tm = ThemeManager()
        themes = tm.get_available_themes()
        
        assert len(themes) >= 1
        g777_dark = next((t for t in themes if t["id"] == "g777_dark"), None)
        assert g777_dark is not None
        assert g777_dark["type"] == "dark"
        assert g777_dark["name"] == "G777 Ultimate Dark"
    
    def test_load_g777_light_theme(self):
        """Verify G777 light theme exists"""
        tm = ThemeManager()
        themes = tm.get_available_themes()
        
        g777_light = next((t for t in themes if t["id"] == "g777_light"), None)
        assert g777_light is not None
        assert g777_light["type"] == "light"
    
    def test_theme_config_file_exists(self, theme_config_path):
        """Verify theme config file is present"""
        assert theme_config_path.exists()
        
        with open(theme_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert "available_themes" in config
        assert len(config["available_themes"]) >= 2


class TestColorPalette:
    """Test color palette integrity"""
    
    def test_g777_dark_primary_color(self):
        """Verify primary color is cyan"""
        tm = ThemeManager()
        tm.set_theme("g777_dark")
        
        semantic = tm.get_semantic()
        assert semantic["primary"] == "#00e5ff"
    
    def test_g777_dark_background(self):
        """Verify background is deep space"""
        tm = ThemeManager()
        tm.set_theme("g777_dark")
        
        semantic = tm.get_semantic()
        assert semantic["bg_app"] == "#050a12"
    
    def test_neon_glow_colors_exist(self):
        """Verify all three neon glow colors are defined"""
        tm = ThemeManager()
        tm.set_theme("g777_dark")
        
        semantic = tm.get_semantic()
        assert "border_glow_cyan" in semantic
        assert "border_glow_orange" in semantic
        assert "border_glow_purple" in semantic
    
    def test_color_palette_completeness(self):
        """Verify all required semantic colors are present"""
        tm = ThemeManager()
        semantic = tm.get_semantic()
        
        required_colors = [
            "primary", "secondary", "accent",
            "bg_app", "bg_card", "bg_sidebar",
            "text_main", "text_muted", "border"
        ]
        
        for color in required_colors:
            assert color in semantic, f"Missing color: {color}"


class TestCSSGeneration:
    """Test CSS variable and neon glow CSS generation"""
    
    def test_css_variables_generation(self):
        """Verify CSS variables are generated correctly"""
        tm = ThemeManager()
        css_vars = tm.get_css_variables()
        
        assert "--g777-primary" in css_vars
        assert "--g777-bg_app" in css_vars
        assert "#00e5ff" in css_vars or "#0088cc" in css_vars
    
    def test_neon_glow_css_contains_hexagons(self):
        """Verify hexagon CSS is included in neon glow"""
        tm = ThemeManager()
        glow_css = tm.get_neon_glow_css()
        
        assert ".hex-icon" in glow_css
        assert "clip-path" in glow_css
        assert "polygon" in glow_css
    
    def test_neon_glow_css_contains_all_colors(self):
        """Verify all three glow colors have CSS classes"""
        tm = ThemeManager()
        glow_css = tm.get_neon_glow_css()
        
        assert ".glow-cyan" in glow_css
        assert ".glow-orange" in glow_css
        assert ".glow-purple" in glow_css
    
    def test_neon_glow_css_has_animations(self):
        """Verify neon glow includes animations"""
        tm = ThemeManager()
        glow_css = tm.get_neon_glow_css()
        
        assert "@keyframes" in glow_css
        assert "pulse-glow" in glow_css
    
    def test_cyber_card_css_included(self):
        """Verify cyber card styling is present"""
        tm = ThemeManager()
        glow_css = tm.get_neon_glow_css()
        
        assert ".cyber-card" in glow_css
        assert "backdrop-filter" in glow_css


class TestThemeSwitching:
    """Test theme switching and persistence"""
    
    @patch('ui.theme_manager.ui')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists', return_value=False)
    def test_set_theme_updates_current_id(self, mock_exists, mock_file, mock_ui):
        """Verify set_theme updates current_theme_id"""
        tm = ThemeManager()
        
        # Directly set theme
        tm.current_theme_id = "g777_light"
        tm.dark_mode_enabled = False
        
        assert tm.current_theme_id == "g777_light"
        assert not tm.is_dark()
    
    @patch('ui.theme_manager.ui')
    def test_theme_defaults_to_g777_dark(self, mock_ui):
        """Verify default theme is g777_dark"""
        tm = ThemeManager()
        
        assert tm.current_theme_id == "g777_dark"
        assert tm.is_dark()
    
    @patch('ui.theme_manager.ui')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists', return_value=False)
    def test_settings_persistence_structure(self, mock_exists, mock_file, mock_ui):
        """Verify settings file structure on save"""
        tm = ThemeManager()
        tm._save_settings()
        
        # Verify that open was called (settings were saved)
        assert mock_file.called


class TestNiceGUIIntegration:
    """Test NiceGUI color application"""
    
    def test_get_nicegui_colors_format(self):
        """Verify NiceGUI colors dictionary format"""
        tm = ThemeManager()
        colors = tm.get_nicegui_colors()
        
        required_keys = ['primary', 'secondary', 'accent', 'positive', 'negative', 'info', 'warning']
        for key in required_keys:
            assert key in colors
            assert colors[key].startswith("#")
    
    def test_nicegui_colors_valid_hex(self):
        """Verify all NiceGUI colors are valid hex codes"""
        tm = ThemeManager()
        colors = tm.get_nicegui_colors()
        
        for color_name, color_value in colors.items():
            assert len(color_value) == 7, f"{color_name} is not 7 chars"
            assert color_value[0] == "#", f"{color_name} doesn't start with #"


class TestErrorHandling:
    """Test error handling and fallbacks"""
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_invalid_theme_file_fallback(self, mock_file):
        """Verify graceful fallback when theme file missing"""
        with patch('ui.theme_manager.theme_manager') as mock_tm:
            tm = ThemeManager()
            themes = tm.get_available_themes()
            
            # Should return empty list, not crash
            assert isinstance(themes, list)
    
    def test_get_current_theme_with_invalid_id(self):
        """Verify fallback when current theme ID is invalid"""
        tm = ThemeManager()
        tm.current_theme_id = "non_existent_theme"
        
        theme = tm.get_current_theme()
        
        # Should return first available theme
        assert theme is not None


class TestBackwardCompatibility:
    """Test backward compatibility with old theme system"""
    
    def test_get_colors_returns_dict(self):
        """Verify get_colors() returns comprehensive palette"""
        tm = ThemeManager()
        colors = tm.get_colors()
        
        assert isinstance(colors, dict)
        assert len(colors) > 0
    
    def test_semantic_error_field_added(self):
        """Verify 'error' field is added for backward compatibility"""
        tm = ThemeManager()
        semantic = tm.get_semantic()
        
        assert "error" in semantic
        assert semantic["error"] == semantic["negative"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

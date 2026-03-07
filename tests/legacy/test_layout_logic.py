"""
Unit Tests for layout.py
Tests navigation, page loading, and error handling logic
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from ui.layout import AntigravityLayout


class TestLayoutInitialization:
    """Test layout initialization"""
    
    @patch('ui.layout.theme_manager')
    @patch('ui.layout.lang_manager')
    def test_layout_creates_successfully(self, mock_lang, mock_theme):
        """Verify layout initializes without errors"""
        layout = AntigravityLayout()
        
        assert layout.current_page == "whatsapp_pairing"
        assert layout.content_container is None
        assert layout.nav_buttons == {}
    
    @patch('ui.layout.theme_manager')
    @patch('ui.layout.lang_manager')
    def test_layout_has_theme_and_lang(self, mock_lang, mock_theme):
        """Verify layout has theme and language managers"""
        layout = AntigravityLayout()
        
        assert layout.theme is not None
        assert layout.lang is not None


class TestPageNavigation:
    """Test page navigation logic"""
    
    @patch('ui.layout.theme_manager')
    @patch('ui.layout.lang_manager')
    @patch('ui.layout.ui')
    def test_navigate_to_changes_current_page(self, mock_ui, mock_lang, mock_theme):
        """Verify navigation updates current page"""
        layout = AntigravityLayout()
        
        # Create a mock container with __enter__ and __exit__
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        mock_container.clear = MagicMock()
        
        # Mock ui.column to return our mock container
        mock_ui.column.return_value = mock_container
        layout.content_container = mock_container
        
        layout.navigate_to("crm_dashboard")
        
        assert layout.current_page == "crm_dashboard"
        assert layout.content_container.clear.called
    
    @patch('ui.layout.theme_manager')
    @patch('ui.layout.lang_manager')
    def test_navigate_without_container_safe(self, mock_lang, mock_theme):
        """Verify navigation is safe when container is None"""
        layout = AntigravityLayout()
        layout.content_container = None
        
        # Should not crash
        layout.navigate_to("crm_dashboard")
        assert layout.current_page == "crm_dashboard"


class TestToolSwitching:
    """Test WhatsApp tool tab switching"""
    
    @patch('ui.layout.theme_manager')
    @patch('ui.layout.lang_manager')
    def test_switch_tool_updates_current_tool(self, mock_lang, mock_theme):
        """Verify tool switching updates state"""
        layout = AntigravityLayout()
        layout.tool_tabs = {
            "group_sender": Mock(),
            "number_filter": Mock()
        }
        
        layout.switch_tool("number_filter")
        
        assert layout.current_tool == "number_filter"


class TestErrorHandling:
    """Test error rendering and handling"""
    
    @patch('ui.layout.theme_manager')
    @patch('ui.layout.lang_manager')
    @patch('ui.layout.ui')
    def test_render_placeholder_for_unknown_page(self, mock_ui, mock_lang, mock_theme):
        """Verify placeholder renders for unimplemented pages"""
        mock_theme.get_semantic.return_value = {
            "accent": "#ff8c00",
            "text_main": "#e0f7ff"
        }
        
        layout = AntigravityLayout()
        layout._render_placeholder("unknown_page")
        
        # Should create UI elements without crashing
        assert mock_ui.column.called
    
    @patch('ui.layout.theme_manager')
    @patch('ui.layout.lang_manager')
    @patch('ui.layout.ui')
    def test_render_error_displays_details(self, mock_ui, mock_lang, mock_theme):
        """Verify error state renders with details"""
        mock_theme.get_semantic.return_value = {
            "negative": "#ff4757",
            "text_main": "#e0f7ff"
        }
        
        layout = AntigravityLayout()
        layout._render_error("test_page", "Test Error", "Full Stack Trace")
        
        # Should display error UI
        assert mock_ui.column.called
        assert mock_ui.icon.called


class TestThemeApplication:
    """Test theme application logic"""
    
    @patch('ui.layout.ui')
    @patch('ui.layout.theme_manager')
    @patch('ui.layout.lang_manager')
    def test_apply_theme_sets_colors(self, mock_lang, mock_theme, mock_ui):
        """Verify theme application sets NiceGUI colors"""
        mock_theme.get_semantic.return_value = {
            "bg_app": "#050a12",
            "text_main": "#e0f7ff"
        }
        mock_theme.get_nicegui_colors.return_value = {
            "primary": "#00e5ff",
            "secondary": "#0a1628",
            "accent": "#ff8c00",
            "positive": "#00ff88",
            "negative": "#ff4757",
            "info": "#00e5ff",
            "warning": "#ff8c00"
        }
        mock_theme.get_css_variables.return_value = "--g777-primary: #00e5ff;"
        mock_theme.get_neon_glow_css.return_value = ".glow-cyan { }"
        
        layout = AntigravityLayout()
        layout.apply_theme()
        
        # Should call ui.colors()
        assert mock_ui.colors.called
        assert mock_ui.add_head_html.called


class TestHeaderCreation:
    """Test header rendering"""
    
    @patch('ui.layout.ui')
    @patch('ui.layout.theme_manager')
    @patch('ui.layout.lang_manager')
    def test_create_header_renders_logo(self, mock_lang, mock_theme, mock_ui):
        """Verify header contains G777 logo"""
        mock_theme.get_semantic.return_value = {
            "bg_header": "#050a12",
            "border": "#1a3a5c",
            "text_muted": "#8cb4d4",
            "primary": "#00e5ff",
            "accent": "#ff8c00"
        }
        mock_lang.get.return_value = "G777 Ultimate"
        
        layout = AntigravityLayout()
        layout.create_header()
        
        # Should create header components
        assert mock_ui.header.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

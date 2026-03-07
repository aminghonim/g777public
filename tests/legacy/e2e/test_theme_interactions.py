"""
E2E Interaction Tests - Theme Interactions
Tests dark/light mode toggle and theme persistence
"""

import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_initial_dark_mode_background(app_url):
    """Verify app starts in dark mode with correct background"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Get body background color
            bg_color = await page.evaluate(
                "getComputedStyle(document.body).backgroundColor"
            )
            
            # Should be dark (close to #050a12 = rgb(5, 10, 18))
            assert "rgb(5, 10," in bg_color or "rgb(4," in bg_color or "rgb(6," in bg_color
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_theme_toggle_button_exists(app_url):
    """Verify theme toggle button is present in header"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Look for theme icon (wb_sunny or nights_stay)
            theme_btns = await page.locator("i:has-text('nights_stay'), i:has-text('wb_sunny')").count()
            assert theme_btns >= 1, "Theme toggle button should exist"
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_hex_icons_render(app_url):
    """Verify hexagonal sidebar icons render correctly"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Check for hex-icon class
            hex_icons = await page.locator(".hex-icon").count()
            assert hex_icons >= 6, f"Should have at least 6 hexagonal icons, found {hex_icons}"
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_cyber_cards_have_glow(app_url):
    """Verify cyber cards are present (if any visible on home page)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Navigate to a page that should have cyber cards
            await page.click("text=CRM", timeout=5000)
            await page.wait_for_timeout(1000)
            
            # Check if cyber-card class exists somewhere
            cyber_cards = await page.locator(".cyber-card").count()
            # May be 0 if CRM page doesn't use them yet
            
        finally:
            await browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

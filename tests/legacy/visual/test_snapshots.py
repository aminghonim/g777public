"""
Visual Regression Tests using Playwright Snapshots
Captures baseline screenshots for comparison
"""

import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_homepage_dark_visual(app_url):
    """Capture homepage in dark mode"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)  # Let animations settle
            
            # Take screenshot
            await page.screenshot(path="tests/frontend/visual/baselines/homepage-dark.png")
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_sidebar_hexagons_visual(app_url):
    """Capture sidebar with hexagonal icons"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1000)
            
            # Locate sidebar and screenshot
            sidebar = page.locator(".hex-icon").first
            if await sidebar.count() > 0:
                await sidebar.screenshot(path="tests/frontend/visual/baselines/sidebar-icon.png")
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_top_navigation_visual(app_url):
    """Capture top navigation tabs"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1000)
            
            # Locate navigation tabs
            nav_tabs = page.locator(".nav-tab").first
            if await nav_tabs.count() > 0:
                await nav_tabs.screenshot(path="tests/frontend/visual/baselines/nav-tab.png")
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_crm_page_visual(app_url):
    """Capture CRM Dashboard page"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Navigate to CRM
            await page.click("text=CRM", timeout=5000)
            await page.wait_for_timeout(2000)
            
            # Capture
            await page.screenshot(path="tests/frontend/visual/baselines/crm-page.png")
            
        finally:
            await browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

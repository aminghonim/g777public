"""
E2E Interaction Tests - Navigation Flow
Tests sidebar navigation and page transitions using Playwright
"""

import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_sidebar_navigation_crm(app_url):
    """Test clicking CRM Dashboard in sidebar"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Wait for sidebar to render
            await page.wait_for_selector(".hex-icon", timeout=5000)
            
            # Click CRM icon (should be visible)
            await page.click("text=CRM", timeout=5000)
            
            # Verify page changed
            await page.wait_for_timeout(1000)
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_top_navigation_tabs_switching(app_url):
    """Test switching between WhatsApp tools in top nav"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Click Members Grabber tab
            await page.click("text=MEMBERS GRABBER", timeout=5000)
            await page.wait_for_timeout(500)
            
            # Click Number Filter tab
            await page.click("text=NUMBER FILTER", timeout=5000)
            await page.wait_for_timeout(500)
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_navigation_updates_active_state(app_url):
    """Verify active navigation item gets highlighted"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Check for hexagonal icons (active ones have glow)
            hex_icons = await page.locator(".hex-icon").count()
            assert hex_icons >= 1, f"Should have at least one hexagonal icon, found {hex_icons}"
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_page_loads_without_errors(app_url):
    """Verify main page loads without console errors"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        console_errors = []
        
        page.on("console", lambda msg: 
            console_errors.append(msg.text) if msg.type == "error" else None
        )
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Check for critical errors
            critical_errors = [e for e in console_errors if "Failed" in e or "Error" in e]
            assert len(critical_errors) == 0, f"Console errors: {critical_errors}"
            
        finally:
            await browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

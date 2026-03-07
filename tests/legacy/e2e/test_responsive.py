"""
Environment Compatibility - Responsive Design Tests
Tests UI on different viewport sizes using Playwright
"""

import pytest
from playwright.async_api import async_playwright


VIEWPORTS = {
    'laptop_old': {'width': 1366, 'height': 768},
    'laptop_hd': {'width': 1920, 'height': 1080},
    '4k': {'width': 3840, 'height': 2160},
    'tablet': {'width': 768, 'height': 1024},
    'mobile': {'width': 375, 'height': 812},
}


@pytest.fixture
def app_url():
    return "http://localhost:8080"


class TestResponsiveDesign:
    """Test UI responsiveness across different screen sizes"""
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.parametrize("viewport_name,viewport", [
        ('laptop_old', VIEWPORTS['laptop_old']),
        ('4k', VIEWPORTS['4k']),
    ])
    async def test_sidebar_no_overlap(self, app_url, viewport_name, viewport):
        """Sidebar elements should not overlap on different screens"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport=viewport)
            
            try:
                await page.goto(app_url, timeout=15000)
                await page.wait_for_load_state("networkidle")
                
                # Check sidebar exists and is visible
                sidebar = page.locator('.sidebar, [class*="sidebar"], aside')
                if await sidebar.count() > 0:
                    box = await sidebar.first.bounding_box()
                    if box:
                        assert box['width'] > 0, f"Sidebar width is 0 on {viewport_name}"
                        assert box['width'] < viewport['width'] * 0.5, "Sidebar too wide"
                
                # Take screenshot for visual verification
                await page.screenshot(path=f"responsive_{viewport_name}.png")
                
            finally:
                await browser.close()
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_cards_layout_laptop_old(self, app_url):
        """Cards should display properly on 1366x768"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport=VIEWPORTS['laptop_old'])
            
            try:
                await page.goto(app_url, timeout=15000)
                await page.wait_for_load_state("networkidle")
                
                # Check for horizontal overflow
                overflow = await page.evaluate('''() => {
                    return document.body.scrollWidth > document.body.clientWidth
                }''')
                
                assert not overflow, "Horizontal overflow detected on 1366x768"
                
            finally:
                await browser.close()
    
    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_4k_scaling(self, app_url):
        """Text and elements should scale properly on 4K"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport=VIEWPORTS['4k'])
            
            try:
                await page.goto(app_url, timeout=15000)
                await page.wait_for_load_state("networkidle")
                
                # Check main content area fills space
                main = page.locator('main, .main-content, [class*="content"]')
                if await main.count() > 0:
                    box = await main.first.bounding_box()
                    if box:
                        assert box['width'] > 1000, "Content area too narrow on 4K"
                
            finally:
                await browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

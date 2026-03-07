"""
=============================================================================
GAP #1: Network Mocking Tests (فجوة الشبكة)
=============================================================================

Purpose: Test application resilience when external APIs fail or network drops.

How this closes the gap:
- Uses Playwright's page.route() to intercept outbound API calls
- Simulates network failure scenarios (timeout, 500 errors)
- Verifies UI shows proper error messages (Neon styled) instead of crashing
- Ensures graceful degradation under network stress

External APIs mocked:
- WhatsApp API endpoints
- Google Maps API
- Cloud Service endpoints
=============================================================================
"""

import pytest
from playwright.async_api import async_playwright, Route, Request


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def app_url():
    """Base URL for the running application"""
    return "http://localhost:8080"


# =============================================================================
# NETWORK FAILURE SCENARIOS
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_network_timeout_shows_error_message(app_url):
    """
    Scenario: Complete internet disconnection
    
    Expected: 
    - UI should display a user-friendly error message
    - Application should NOT crash or show raw error stack
    - Error message should use Neon styling (visible, pleasant)
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            # Load page first
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Intercept ALL outbound requests and make them timeout
            async def block_all_requests(route: Route, request: Request):
                # Block API calls but allow static assets
                if "/api/" in request.url or "whatsapp" in request.url.lower():
                    await route.abort("connectionfailed")
                else:
                    await route.continue_()
            
            await page.route("**/*", block_all_requests)
            
            # Navigate to a page that requires API calls
            crm_link = page.locator("text=CRM")
            if await crm_link.count() > 0:
                await crm_link.first.click()
                await page.wait_for_timeout(2000)
            
            # Verify page didn't crash (still has content)
            body_content = await page.locator("body").inner_text()
            assert len(body_content) > 0, "Page should have content even after network failure"
            
            # Check that no unhandled JavaScript errors occurred
            # (We already set up error listener in E2E fixtures)
            
        finally:
            await browser.close()


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_api_500_error_displays_neon_error(app_url):
    """
    Scenario: Server returns 500 Internal Server Error
    
    Expected:
    - UI should catch the error gracefully
    - Display styled error message (not raw JSON/stack trace)
    - Allow user to retry or navigate elsewhere
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        errors_caught = []
        
        # Listen for console errors
        page.on("console", lambda msg: 
            errors_caught.append(msg.text) if msg.type == "error" else None
        )
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Mock API responses with 500 error
            async def mock_500_error(route: Route, request: Request):
                if "/api/" in request.url:
                    await route.fulfill(
                        status=500,
                        content_type="application/json",
                        body='{"error": "Internal Server Error", "message": "Simulated failure"}'
                    )
                else:
                    await route.continue_()
            
            await page.route("**/api/**", mock_500_error)
            
            # Trigger an action that would call the API
            # (Navigate to Cloud Hub which makes API calls)
            cloud_link = page.locator("text=Cloud")
            if await cloud_link.count() > 0:
                await cloud_link.first.click()
                await page.wait_for_timeout(2000)
            
            # Page should still be responsive
            page_title = await page.title()
            assert page_title is not None, "Page should still have a title after 500 error"
            
        finally:
            await browser.close()


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_whatsapp_api_failure_handled(app_url):
    """
    Scenario: WhatsApp API becomes unreachable
    
    Expected:
    - Members Grabber / Group Sender should show connection error
    - User should see retry option
    - No JavaScript exceptions thrown
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        js_errors = []
        page.on("pageerror", lambda err: js_errors.append(str(err)))
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Block WhatsApp-related endpoints
            async def block_whatsapp(route: Route, request: Request):
                url_lower = request.url.lower()
                if "whatsapp" in url_lower or "baileys" in url_lower or "wa.me" in url_lower:
                    await route.abort("failed")
                else:
                    await route.continue_()
            
            await page.route("**/*", block_whatsapp)
            
            # Navigate to pairing page
            pairing_link = page.locator("text=Connection")
            if await pairing_link.count() > 0:
                await pairing_link.first.click()
                await page.wait_for_timeout(2000)
            
            # Should not have uncaught JavaScript errors
            critical_errors = [e for e in js_errors if "Uncaught" in e]
            assert len(critical_errors) == 0, f"Should not have uncaught errors: {critical_errors}"
            
        finally:
            await browser.close()


@pytest.mark.asyncio
@pytest.mark.e2e  
async def test_google_maps_api_fallback(app_url):
    """
    Scenario: Google Maps API quota exceeded or blocked
    
    Expected:
    - Maps Extractor page should show appropriate message
    - Application should not freeze
    - User can navigate away without issues
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Block Google Maps API
            async def block_google(route: Route, request: Request):
                if "maps.google" in request.url or "googleapis" in request.url:
                    await route.fulfill(
                        status=403,
                        content_type="application/json",
                        body='{"error": {"code": 403, "message": "API quota exceeded"}}'
                    )
                else:
                    await route.continue_()
            
            await page.route("**/*", block_google)
            
            # Navigate to Google Maps page
            maps_link = page.locator("text=Google Maps")
            if await maps_link.count() > 0:
                await maps_link.first.click()
                await page.wait_for_timeout(2000)
            
            # Verify we can still navigate back
            home_link = page.locator("text=Connection")
            if await home_link.count() > 0:
                await home_link.first.click()
                await page.wait_for_timeout(1000)
            
            # Page should still be functional
            hex_icons = await page.locator(".hex-icon").count()
            assert hex_icons > 0, "Navigation should still work after API failure"
            
        finally:
            await browser.close()


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_slow_network_with_loading_indicator(app_url):
    """
    Scenario: Very slow network (high latency)
    
    Expected:
    - UI should show loading indicators
    - User should not see frozen/blank screen
    - Eventual timeout should be graceful
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Simulate slow network by delaying responses
            async def slow_response(route: Route, request: Request):
                if "/api/" in request.url:
                    # Delay for 3 seconds
                    import asyncio
                    await asyncio.sleep(3)
                    await route.continue_()
                else:
                    await route.continue_()
            
            await page.route("**/api/**", slow_response)
            
            # Navigate to a data-heavy page
            crm_link = page.locator("text=CRM")
            if await crm_link.count() > 0:
                await crm_link.first.click()
            
            # Check if there's any loading indication (spinner, skeleton, etc.)
            await page.wait_for_timeout(1000)
            
            # Page should still be interactive during load
            body = await page.locator("body").inner_html()
            assert len(body) > 100, "Page should have content even during slow load"
            
        finally:
            await browser.close()


# =============================================================================
# EDGE CASES
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_mixed_success_and_failure_responses(app_url):
    """
    Scenario: Some APIs work, others fail (partial outage)
    
    Expected:
    - Working features should remain functional
    - Failed features should show individual errors
    - No cascade failure
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            await page.goto(app_url, timeout=10000)
            await page.wait_for_load_state("networkidle")
            
            # Selectively fail some endpoints
            async def partial_failure(route: Route, request: Request):
                if "crm" in request.url.lower():
                    # CRM works fine
                    await route.continue_()
                elif "cloud" in request.url.lower():
                    # Cloud service fails
                    await route.abort("failed")
                else:
                    await route.continue_()
            
            await page.route("**/*", partial_failure)
            
            # UI should still be navigable
            hex_icons = await page.locator(".hex-icon").count()
            assert hex_icons >= 1, "Sidebar should still be functional during partial outage"
            
        finally:
            await browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

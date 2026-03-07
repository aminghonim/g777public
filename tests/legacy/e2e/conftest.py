"""
Shared fixtures for E2E tests
"""

import pytest


@pytest.fixture(scope="session")
def app_url():
    """Base URL for testing - app must be running"""
    return "http://localhost:8080"


@pytest.fixture
def browser_context_args(browser_context_args):
    """Configure browser for testing"""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    }

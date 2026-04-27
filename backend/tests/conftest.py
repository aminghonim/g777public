"""
pytest Configuration with RTK Enforcement

This file runs before any tests. It:
1. Enables RTK enforcement guard
2. Provides fixtures for testing with/without enforcement
3. Logs any violations during test execution
"""

import pytest
import logging
import sys
from typing import Generator

# =====================================================================
# RTK Enforcement Setup
# =====================================================================

from backend.core.rtk_enforcement import (
    install_enforcement_guard,
    TemporaryEnforcementBypass,
)

logger = logging.getLogger("g777.tests")

# Install enforcement for ALL tests (runs once during setup)
# We use WARNING level to keep noise low unless a violation occurs
install_enforcement_guard(block_violations=True, log_level="WARNING")


# =====================================================================
# Pytest Fixtures
# =====================================================================

@pytest.fixture(scope="session")
def rtk_enforcement_enabled():
    """Fixture that verifies RTK enforcement is enabled."""
    return True


@pytest.fixture
def allow_subprocess():
    """Fixture that temporarily disables RTK enforcement for a single test."""
    with TemporaryEnforcementBypass():
        yield
    # Enforcement re-enabled after test


@pytest.fixture
def executor_fixture():
    """Fixture providing a SystemCommandExecutor for testing."""
    from backend.core.system_commands import SystemCommandExecutor
    return SystemCommandExecutor("test_tenant")


# =====================================================================
# Pytest Hooks
# =====================================================================

def pytest_configure(config):
    """
    Pytest hook: Called before test collection.
    Register custom test markers.
    """
    config.addinivalue_line(
        "markers",
        "subprocess: mark test as needing direct subprocess access (bypass enforcement)",
    )
    config.addinivalue_line(
        "markers",
        "rtk_enforcement: mark test as verifying RTK enforcement behavior",
    )
    
    logger.info("✓ RTK Enforcement Guard active for test suite")


def pytest_runtest_makereport(item, call):
    """
    Pytest hook: Called after each test phase.
    Logs enforcement violations for diagnostics.
    """
    if call.excinfo and "SystemCommandExecutor" in str(call.excinfo.value):
        logger.error(
            f"RTK Enforcement violation in test: {item.nodeid}",
            extra={"error": str(call.excinfo.value)},
        )

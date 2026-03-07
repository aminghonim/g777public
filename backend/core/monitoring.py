"""
Monitoring Module - Centralized Sentry Integration
"""

import os
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger(__name__)


def init_monitoring():
    """Initialize Sentry SDK with FastAPI integration."""
    sentry_dsn = os.getenv("SENTRY_DSN")

    if not sentry_dsn:
        logger.warning("[MONITORING] SENTRY_DSN not found. Monitoring disabled.")
        return

    # Configure logging integration
    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors and above as events
    )

    try:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FastApiIntegration(), sentry_logging],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.2")),
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of transactions.
            profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.2")),
            environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
            send_default_pii=True,
        )
        logger.info("[MONITORING] Sentry initialized successfully.")
    except Exception as e:
        logger.error(f"[MONITORING] Failed to initialize Sentry: {e}")


def capture_exception(e: Exception):
    """Shorthand to capture an exception manually."""
    sentry_sdk.capture_exception(e)


def capture_message(msg: str, level: str = "info"):
    """Shorthand to capture a message manually."""
    sentry_sdk.capture_message(msg, level=level)

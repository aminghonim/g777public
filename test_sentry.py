import os
import sys
from dotenv import load_dotenv
import sentry_sdk

# Load .env file
load_dotenv(".env")

from backend.core.monitoring import init_monitoring, capture_exception

print("Initializing Sentry...")
init_monitoring()

try:
    print("Triggering test exception...")
    # This will cause a ZeroDivisionError
    1 / 0
except Exception as e:
    print(f"Exception caught: {e}")
    print("Sending exception to Sentry...")
    capture_exception(e)
    # Ensure the event is sent before the script exits
    sentry_sdk.flush(timeout=5.0)

print("Test complete! Please check your Sentry dashboard for a 'ZeroDivisionError'.")

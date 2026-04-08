from google import adk
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_adk_import():
    try:
        # Checking if adk is present in the google namespace
        if hasattr(adk, "__path__"):
            logger.info(
                "SUCCESS: Google ADK Library is correctly installed and accessible via 'google.adk'."
            )
            logger.info(f"Location: {adk.__path__}")
        else:
            logger.warning(
                "Import successful but 'adk' child module not found in 'google' namespace."
            )
    except Exception as e:
        logger.error(f"Error during ADK verification: {e}")


if __name__ == "__main__":
    test_adk_import()

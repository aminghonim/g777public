import os
import logging
import requests
from dotenv import load_dotenv

# Configure logging per GEMINI.md Rule 7
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

load_dotenv("/home/g777/MYCOMPUTER/work/2/.env")

EVO_URL = os.getenv("EVOLUTION_PUBLIC_URL", "http://localhost:8080")
API_KEY = os.getenv(
    "EVOLUTION_API_KEY", "os.getenv('EVOLUTION_API_KEY', 'your_api_key_here')"
)
INSTANCE = os.getenv("EVOLUTION_INSTANCE_NAME", "G777")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

headers = {"apikey": API_KEY, "Content-Type": "application/json"}


def check_webhook() -> None:
    """
    Check if a webhook is currently configured for the specified instance.
    If not, attempt to set it.
    """
    logger.info(f"Checking Webhook for instance '{INSTANCE}' on {EVO_URL}...")
    try:
        response = requests.get(
            f"{EVO_URL}/webhook/find/{INSTANCE}", headers=headers, timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data and "url" in data:
                logger.info(f"SUCCESS: Webhook is currently set to: {data['url']}")
                logger.info(f"Evolution API will forward messages to: {data['url']}")
            else:
                logger.warning("No Webhook is currently configured for this instance.")
                set_webhook()
        else:
            logger.error(f"Failed to fetch webhook info: {response.text}")
            if response.status_code == 404:
                logger.info("Instance might not exist or the router is offline.")
    except requests.RequestException as e:
        logger.error(f"Connection Error: {e}")


def set_webhook() -> None:
    """
    Configure the webhook URL for the Evolution API instance.
    """
    if not WEBHOOK_URL:
        logger.error("WEBHOOK_URL is missing from .env file!")
        return

    logger.info(f"Attempting to set Webhook to: {WEBHOOK_URL}...")

    payload = {
        "webhook": {
            "url": WEBHOOK_URL,
            "byEvents": False,
            "base64": False,
            "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE", "SEND_MESSAGE"],
        }
    }

    try:
        response = requests.post(
            f"{EVO_URL}/webhook/set/{INSTANCE}",
            headers=headers,
            json=payload,
            timeout=10,
        )
        if response.status_code in [200, 201]:
            logger.info(
                "SUCCESS: Webhook configured successfully! The Pipeline is now CONNECTED."
            )
        else:
            logger.error(f"Failed to set webhook: {response.text}")
    except requests.RequestException as e:
        logger.error(f"Connection Error: {e}")


if __name__ == "__main__":
    check_webhook()

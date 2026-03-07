import os
import time
import logging

import requests
from dotenv import load_dotenv

# Configure logging per GEMINI.md Rule 7
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

load_dotenv("/home/g777/MYCOMPUTER/work/2/.env")

EVO_URL = "http://localhost:8080"
API_KEY = os.getenv("EVOLUTION_API_KEY", "antigravity_secret_key_2024")
INSTANCE = os.getenv("EVOLUTION_INSTANCE_NAME", "G777")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

headers = {"apikey": API_KEY, "Content-Type": "application/json"}


def wait_for_evolution() -> bool:
    """
    Poll the Evolution API until it is ready or timeout occurs.
    """
    logger.info("Waiting for Evolution API to be ready...")
    for _ in range(30):
        try:
            response = requests.get(
                f"{EVO_URL}/instance/fetchInstances", headers=headers, timeout=10
            )
            if response.status_code == 200:
                logger.info("SUCCESS: Evolution API is ONLINE.")
                return True
        except requests.RequestException:
            pass
        time.sleep(2)
    return False


def setup() -> None:
    """
    Create the Evolution API instance and configure the webhook.
    """
    if not wait_for_evolution():
        logger.error("Evolution API did not start in time.")
        return

    # 1. Create Instance
    logger.info(f"Creating instance '{INSTANCE}'...")
    payload = {
        "instanceName": INSTANCE,
        "token": API_KEY,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS",
    }

    res = requests.post(
        f"{EVO_URL}/instance/create", headers=headers, json=payload, timeout=10
    )
    if res.status_code in [200, 201]:
        logger.info(f"SUCCESS: Instance '{INSTANCE}' created successfully.")
    else:
        logger.warning(f"Could not create instance (might already exist): {res.text}")

    # 2. Set Webhook
    if WEBHOOK_URL:
        logger.info(f"Setting global webhook to: {WEBHOOK_URL}...")
        webhook_payload = {
            "webhook": {
                "enabled": True,
                "url": WEBHOOK_URL,
                "byEvents": False,
                "base64": False,
                "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE", "SEND_MESSAGE"],
            }
        }
        res = requests.post(
            f"{EVO_URL}/webhook/set/{INSTANCE}",
            headers=headers,
            json=webhook_payload,
            timeout=10,
        )
        if res.status_code in [200, 201]:
            logger.info("SUCCESS: Webhook configured.")
        else:
            logger.error(f"Webhook configuration failed: {res.text}")


if __name__ == "__main__":
    setup()

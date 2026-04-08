import logging
from backend.whatsapp_sender import WhatsAppSender
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_sender_init():
    try:
        sender = WhatsAppSender()
        logger.info("[OK] WhatsAppSender initialized")
        logger.info(f"[*] Cloud Service: {sender.cloud}")
        return True
    except Exception as e:
        logger.error(f"[FAIL] WhatsAppSender failed to initialize: {e}")
        return False


if __name__ == "__main__":
    test_sender_init()

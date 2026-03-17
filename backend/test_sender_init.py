from backend.whatsapp_sender import WhatsAppSender
import os


def test_sender_init():
    try:
        sender = WhatsAppSender()
        print("[OK] WhatsAppSender initialized")
        print(f"[*] Cloud Service: {sender.cloud}")
        return True
    except Exception as e:
        print(f"[FAIL] WhatsAppSender failed to initialize: {e}")
        return False


if __name__ == "__main__":
    test_sender_init()

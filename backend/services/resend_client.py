import os
import resend
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

class ResendClient:
    """
    Modular client to handle transactional emails via Resend API.
    Adheres to Rule 5 (Modular Integrity) and Rule 6 (Resilience via Tenacity).
    """

    def __init__(self):
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            logger.warning("RESEND_API_KEY not found in environment. Emails will be disabled.")
        resend.api_key = api_key
        self.default_sender = os.getenv("RESEND_DEFAULT_SENDER", "onboarding@resend.dev")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> dict:
        """
        Send an email using Resend with retry logic.
        """
        if not resend.api_key:
            return {"error": "Missing API Key", "status": "failed"}

        try:
            params = {
                "from": self.default_sender,
                "to": to_email if isinstance(to_email, list) else [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content or html_content,
            }
            logger.info(f"Sending email to {to_email} via Resend...")
            response = resend.Emails.send(params)
            logger.info("Email sent successfully.")
            return {"data": response, "status": "success"}
        except Exception as e:
            logger.error(f"Failed to send email via Resend: {str(e)}")
            raise e  # Re-raise to trigger tenacity retry

# Singleton instance
resend_client = ResendClient()

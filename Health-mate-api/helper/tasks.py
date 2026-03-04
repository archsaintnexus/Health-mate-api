import os
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_a_mail(self, title: str, message: str, to: str, is_html: bool = False) -> dict:
    import requests

    api_key = os.getenv('RESEND_API_KEY')
    if not api_key:
        raise ValueError("RESEND_API_KEY environment variable is not set")

    sender = os.getenv('RESEND_FROM_EMAIL', 'noreply@ordfellow.com')

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "from": sender,
        "to": to,
        "subject": title,
    }

    if is_html:
        payload["html"] = message
    else:
        payload["text"] = message

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            json=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        logger.info(f"Email sent successfully to {to} | subject: {title}")
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        raise self.retry(exc=e)

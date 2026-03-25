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

@shared_task
def mark_missed_consultations():
    """
    Runs every 30 minutes via Celery Beat.
    Marks consultations as missed if:
    - Status is still scheduled
    - Scheduled time + 60 minutes has passed
    """
    from datetime import timedelta
    from django.utils import timezone
    from consultation.models import Consultation, ConsultationStatus

    cutoff = timezone.now() - timedelta(minutes=60)

    missed = Consultation.objects.filter(
        status=ConsultationStatus.SCHEDULED,
        scheduled_at__lt=cutoff,
    )
    count = missed.update(status=ConsultationStatus.MISSED)

    logger.info(f"Marked {count} consultations as missed")
    return f"Marked {count} consultations as missed"


@shared_task
def cleanup_expired_rooms():
    """
    Runs every hour via Celery Beat.
    Cleans up any Daily.co rooms for completed
    or cancelled consultations that still have rooms.
    """
    from consultation.models import Consultation, ConsultationStatus
    from consultation.services import DailyCoService

    consultations = Consultation.objects.filter(
        status__in=[
            ConsultationStatus.COMPLETED,
            ConsultationStatus.CANCELLED,
            ConsultationStatus.MISSED,
        ],
        room_name__isnull=False,
    ).exclude(room_name="")

    count = 0
    for consultation in consultations:
        try:
            DailyCoService.delete_room(consultation.room_name)
            consultation.room_name = ""
            consultation.room_url = ""
            consultation.patient_token = ""
            consultation.doctor_token = ""
            consultation.save(update_fields=[
                "room_name", "room_url",
                "patient_token", "doctor_token"
            ])
            count += 1
        except Exception as e:
            logger.error(
                f"Failed to cleanup room for consultation "
                f"{consultation.id}: {e}"
            )

    logger.info(f"Cleaned up {count} Daily.co rooms")
    return f"Cleaned up {count} Daily.co rooms"

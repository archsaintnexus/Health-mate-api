import requests
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class DailyCoService:
    """Handles all Daily.co API interactions."""

    BASE_URL = settings.DAILY_API_URL
    HEADERS = {
        "Authorization": f"Bearer {settings.DAILY_API_KEY}",
        "Content-Type": "application/json",
    }

    # ── Room Management ──────────────────────────────────────────────────────

    @classmethod
    def create_room(cls, consultation_id: int) -> dict:
        """Create a Daily.co room for a consultation."""
        room_name = f"consultation-{consultation_id}-{uuid.uuid4().hex[:8]}"

        payload = {
            "name": room_name,
            "privacy": "private",
            "properties": {
                "max_participants": 2,
                "enable_chat": True,
                "enable_knocking": False,
                "start_video_off": False,
                "start_audio_off": False,
                "exp": 0,  # No expiry — we control via tokens
            }
        }

        response = requests.post(
            f"{cls.BASE_URL}/rooms",
            json=payload,
            headers=cls.HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "room_name": data["name"],
            "room_url": data["url"],
        }

    @classmethod
    def create_meeting_token(
        cls,
        room_name: str,
        user_id: str,
        user_name: str,
        is_owner: bool = False,
        expiry_minutes: int = 60,
    ) -> str:
        """Create a meeting token for a participant."""
        import time
        exp = int(time.time()) + (expiry_minutes * 60)

        payload = {
            "properties": {
                "room_name": room_name,
                "user_id": str(user_id),
                "user_name": user_name,
                "is_owner": is_owner,
                "exp": exp,
                "enable_screenshare": is_owner,
                "start_video_off": False,
                "start_audio_off": False,
            }
        }

        response = requests.post(
            f"{cls.BASE_URL}/meeting-tokens",
            json=payload,
            headers=cls.HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["token"]

    @classmethod
    def delete_room(cls, room_name: str) -> bool:
        """Delete a Daily.co room after consultation ends."""
        try:
            response = requests.delete(
                f"{cls.BASE_URL}/rooms/{room_name}",
                headers=cls.HEADERS,
                timeout=30,
            )
            return response.status_code == 200
        except Exception:
            return False

    @classmethod
    def get_room_info(cls, room_name: str) -> dict:
        """Get room details from Daily.co."""
        response = requests.get(
            f"{cls.BASE_URL}/rooms/{room_name}",
            headers=cls.HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    # ── Consultation Business Logic ──────────────────────────────────────────

    @classmethod
    def setup_consultation_room(cls, consultation) -> dict:
        """
        Create room and generate tokens for both
        patient and doctor.
        """
        # Create the room
        room_data = cls.create_room(consultation.id)
        room_name = room_data["room_name"]
        room_url = room_data["room_url"]

        # Generate patient token
        patient_token = cls.create_meeting_token(
            room_name=room_name,
            user_id=str(consultation.patient.id),
            user_name=consultation.patient.full_name,
            is_owner=False,
        )

        # Generate doctor token (owner)
        doctor_token = cls.create_meeting_token(
            room_name=room_name,
            user_id=str(consultation.doctor.user.id),
            user_name=f"Dr. {consultation.doctor.user.full_name}",
            is_owner=True,
        )

        return {
            "room_name": room_name,
            "room_url": room_url,
            "patient_token": patient_token,
            "doctor_token": doctor_token,
        }


class ConsultationService:
    """Business logic helpers for consultations."""

    @staticmethod
    def join_consultation(consultation, user) -> dict:
        now = timezone.now()
        window_start = consultation.scheduled_at - timedelta(minutes=15)
        window_end = consultation.scheduled_at + timedelta(minutes=60)

        if not (window_start <= now <= window_end):
            raise ValidationError(
                "Cannot join at this time. "
                "You can join within 15 minutes of your scheduled time."
            )

        if consultation.status in ["completed", "cancelled", "missed"]:
            raise ValidationError("This consultation cannot be joined.")

        if not consultation.room_url:
            room_data = DailyCoService.setup_consultation_room(consultation)
            consultation.room_name = room_data["room_name"]
            consultation.room_url = room_data["room_url"]
            consultation.patient_token = room_data["patient_token"]
            consultation.doctor_token = room_data["doctor_token"]
            consultation.status = "connecting"
            consultation.save(update_fields=[
                "room_name",
                "room_url",
                "patient_token",
                "doctor_token",
                "status",
                "updated_at",
            ])

        is_doctor = hasattr(user, "doctor_profile")
        token = consultation.doctor_token if is_doctor else consultation.patient_token

        return {
            "consultation_id": consultation.id,
            "room_url": consultation.room_url,
            "token": token,
            "status": consultation.status,
            "scheduled_at": consultation.scheduled_at,
        }

    @staticmethod
    def add_notes(consultation_id: int, doctor, data: dict):
        from consultation.models import Consultation, ConsultationNote, ConsultationStatus
        from medicals.models import MedicalRecord

        try:
            consultation = Consultation.objects.get(
                id=consultation_id,
                doctor__user=doctor,
                status=ConsultationStatus.COMPLETED,
            )
        except Consultation.DoesNotExist:
            raise ValidationError("Consultation not found or not yet completed.")

        note, _ = ConsultationNote.objects.update_or_create(
            consultation=consultation,
            defaults={
                "doctor_notes": data.get("doctor_notes", ""),
                "diagnosis": data.get("diagnosis", ""),
                "prescription": data.get("prescription", ""),
                "follow_up_required": data.get("follow_up_required", False),
                "follow_up_date": data.get("follow_up_date"),
                "is_reviewed": True,
            },
        )
        if any(field.name == "status" for field in MedicalRecord._meta.fields):
            MedicalRecord.objects.filter(consultation_id=consultation.id).update(status="available")

        return consultation, note
    
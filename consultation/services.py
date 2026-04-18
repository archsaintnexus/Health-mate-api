import requests
import time
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import DoctorOnboarding, OnboardingStatus

from consultation.models import DoctorProfile, DoctorProfile

from consultation.models import OnboardingStatus
class DailyCoService:
    """Handles all Daily.co API interactions."""

    BASE_URL = settings.DAILY_API_URL
    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {settings.DAILY_API_KEY}",
            "Content-Type": "application/json",
        }

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
                "exp": int(time.time()) + 3600,
            }
        }

        response = requests.post(
            f"{cls.BASE_URL}/rooms",
            json=payload,
            headers=cls.get_headers(),
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
            headers=cls.get_headers(),
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
                headers=cls.get_headers(),
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
            headers=cls.get_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def setup_consultation_room(cls, consultation) -> dict:
        """
        Create room and generate tokens for both
        patient and doctor.
        """
        room_data = cls.create_room(consultation.id)
        room_name = room_data["room_name"]
        room_url = room_data["room_url"]
        patient_token = cls.create_meeting_token(
            room_name=room_name,
            user_id=str(consultation.patient.id),
            user_name=consultation.patient.full_name,
            is_owner=False,
        )

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
        window_start = consultation.scheduled_at - timedelta(minutes=2)
        window_end = consultation.scheduled_at + timedelta(minutes=60)

        if not (window_start <= now <= window_end):
            raise ValidationError(
                "Cannot join at this time. "
                "You can join within 2 minutes of your scheduled time."
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

class OnboardingService:

    @staticmethod
    def get_or_create_doctor_profile(user) -> "DoctorProfile":
        """Get or create DoctorProfile for a provider user."""
        from .models import DoctorProfile, DoctorOnboarding
        profile, _ = DoctorProfile.objects.get_or_create(user=user)
        DoctorOnboarding.objects.get_or_create(doctor=profile)
        return profile

    @staticmethod
    def save_personal_info(user, data: dict) -> "DoctorProfile":
        from .models import DoctorOnboarding
        profile = OnboardingService.get_or_create_doctor_profile(user)
        profile.phone_number = data.get("phone_number", profile.phone_number)
        profile.date_of_birth = data.get("date_of_birth", profile.date_of_birth)
        profile.gender = data.get("gender", profile.gender)
        profile.city = data.get("city", profile.city)
        profile.location = data.get("location", profile.location)
        if data.get("profile_picture"):
            profile.profile_picture = data["profile_picture"]
        profile.save()

        onboarding = profile.onboarding
        onboarding.step_personal_done = True
        onboarding.save(update_fields=["step_personal_done"])
        return profile

    @staticmethod
    def save_professional_info(user, data: dict) -> "DoctorProfile":
        profile = OnboardingService.get_or_create_doctor_profile(user)
        profile.specialty = data.get("specialty", profile.specialty)
        profile.bio = data.get("bio", profile.bio)
        profile.clinical_expertise = data.get("clinical_expertise", profile.clinical_expertise)
        profile.languages = data.get("languages", profile.languages)
        profile.education = data.get("education", profile.education)
        profile.experience_years = data.get("experience_years", profile.experience_years)
        profile.consultation_type = data.get("consultation_type", profile.consultation_type)
        profile.save()

        onboarding = profile.onboarding
        onboarding.step_professional_done = True
        onboarding.save(update_fields=["step_professional_done"])
        return profile

    @staticmethod
    def save_medical_info(user, data: dict) -> "DoctorProfile":
        profile = OnboardingService.get_or_create_doctor_profile(user)
        profile.medical_school = data.get("medical_school", profile.medical_school)
        profile.graduation_year = data.get("graduation_year", profile.graduation_year)
        profile.residency = data.get("residency", profile.residency)
        profile.board_certifications = data.get("board_certifications", profile.board_certifications)
        profile.professional_memberships = data.get("professional_memberships", profile.professional_memberships)
        profile.save()

        onboarding = profile.onboarding
        onboarding.step_medical_done = True
        onboarding.save(update_fields=["step_medical_done"])
        return profile

    @staticmethod
    @transaction.atomic
    def save_availability(user, slots: list) -> "DoctorProfile":
        """
        slots = [
            {"day_of_week": "monday", "start_time": "09:00", "end_time": "17:00"},
            {"day_of_week": "tuesday", "start_time": "09:00", "end_time": "17:00"},
        ]
        """
        from .models import DoctorAvailability
        profile = OnboardingService.get_or_create_doctor_profile(user)
        DoctorAvailability.objects.filter(doctor=profile).delete()
        DoctorAvailability.objects.bulk_create([
            DoctorAvailability(
                doctor=profile,
                day_of_week=slot["day_of_week"],
                start_time=slot["start_time"],
                end_time=slot["end_time"],
                is_active=True,
            )
            for slot in slots
        ])

        onboarding = profile.onboarding
        onboarding.step_availability_done = True
        onboarding.save(update_fields=["step_availability_done"])
        return profile

    @staticmethod
    @transaction.atomic
    def save_documents(user, data: dict) -> "DoctorProfile":
        """
        Final step — save documents and set status to PENDING.
        """
        from .models import DoctorDocument, DoctorOnboarding, OnboardingStatus
        from django.utils import timezone

        profile = OnboardingService.get_or_create_doctor_profile(user)

        doc, _ = DoctorDocument.objects.get_or_create(doctor=profile)
        if data.get("medical_license"):
            doc.medical_license = data["medical_license"]
        if data.get("medical_certificate"):
            doc.medical_certificate = data["medical_certificate"]
        doc.medical_license_number = data.get("medical_license_number", doc.medical_license_number)
        doc.medical_license_expiry = data.get("medical_license_expiry", doc.medical_license_expiry)
        doc.save()
        onboarding = profile.onboarding
        onboarding.step_documents_done = True
        onboarding.status = OnboardingStatus.PENDING
        onboarding.submitted_at = timezone.now()
        onboarding.save(update_fields=[
            "step_documents_done", "status", "submitted_at"
        ])
        from helper.tasks import send_a_mail
        send_a_mail.delay(
            title="Application Under Review — Health Mate",
            message=f"""
            <html>
              <body style="font-family: Arial, sans-serif;">
                <h3>Application Received</h3>
                <p>Dear Dr. {user.full_name},</p>
                <p>Your application has been submitted successfully
                and is currently under review.</p>
                <p>This process typically takes <strong>1-3 business days</strong>.</p>
                <p>We will notify you once a decision has been made.</p>
                <br/>
                <p>The Health Mate Team</p>
              </body>
            </html>
            """,
            to=user.email,
            is_html=True,
        )

        return profile

    @staticmethod
    def get_status(user) -> dict:
        from .models import DoctorOnboarding
        profile = OnboardingService.get_or_create_doctor_profile(user)
        onboarding = profile.onboarding

        return {
            "status": onboarding.status,
            "current_step": onboarding.current_step,
            "can_access_dashboard": onboarding.can_access_dashboard,
            "steps": {
                "personal": onboarding.step_personal_done,
                "professional": onboarding.step_professional_done,
                "medical_info": onboarding.step_medical_done,
                "availability": onboarding.step_availability_done,
                "documents": onboarding.step_documents_done,
            },
            "rejection_reason": onboarding.rejection_reason or None,
            "submitted_at": onboarding.submitted_at,
            "reviewed_at": onboarding.reviewed_at,
        }

    @staticmethod
    @transaction.atomic
    def resubmit(user, data: dict) -> "DoctorProfile":
        """
        Doctor resubmits after rejection.
        Resets status to PENDING.
        """

        profile = OnboardingService.get_or_create_doctor_profile(user)
        onboarding = profile.onboarding

        if onboarding.status != OnboardingStatus.REJECTED:
            raise ValueError("Only rejected applications can be resubmitted.")
        
        OnboardingService.save_documents(user, data)
        onboarding.refresh_from_db()
        onboarding.rejection_reason = ""
        onboarding.status = OnboardingStatus.PENDING
        onboarding.submitted_at = timezone.now()
        onboarding.save(update_fields=[
            "rejection_reason", "status", "submitted_at"
        ])

        return profile
    

    
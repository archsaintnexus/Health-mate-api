import uuid
from django.db import models
from django.utils import timezone
from accounts.models import CompanyUser


class ConsultationStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    CONNECTING = "connecting", "Connecting"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    MISSED = "missed", "Missed"


class ConsultationType(models.TextChoices):
    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"
    CHAT = "chat", "Chat"


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        CompanyUser,
        on_delete=models.CASCADE,
        related_name="doctor_profile"
    )
    specialty = models.CharField(max_length=100)
    bio = models.TextField(blank=True, default="")
    clinical_expertise = models.TextField(blank=True, default="")
    languages = models.CharField(max_length=200, blank=True, default="English")
    education = models.TextField(blank=True, default="")
    experience_years = models.PositiveIntegerField(default=0)
    consultation_type = models.CharField(
        max_length=10,
        choices=ConsultationType.choices,
        default=ConsultationType.VIDEO
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    location = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctor_profiles"
        ordering = ["-rating"]

    def __str__(self):
        return f"Dr. {self.user.full_name} — {self.specialty}"


class Consultation(models.Model):
    patient = models.ForeignKey(
        CompanyUser,
        on_delete=models.CASCADE,
        related_name="patient_consultations"
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="doctor_consultations"
    )
    consultation_type = models.CharField(
        max_length=10,
        choices=ConsultationType.choices,
        default=ConsultationType.VIDEO
    )
    status = models.CharField(
        max_length=20,
        choices=ConsultationStatus.choices,
        default=ConsultationStatus.SCHEDULED
    )

    # Daily.co room details
    room_name = models.CharField(max_length=200, blank=True, default="")
    room_url = models.URLField(blank=True, default="")
    patient_token = models.TextField(blank=True, default="")
    doctor_token = models.TextField(blank=True, default="")

    # Scheduling
    scheduled_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)

    # Additional info
    reason = models.TextField(blank=True, default="")
    patient_notes = models.TextField(blank=True, default="")
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "consultations"
        ordering = ["-scheduled_at"]

    def __str__(self):
        return f"{self.patient.full_name} → Dr.{self.doctor.user.full_name} [{self.status}]"

    @property
    def is_upcoming(self):
        return (
            self.status == ConsultationStatus.SCHEDULED
            and self.scheduled_at > timezone.now()
        )

    @property                          # ← INSIDE the class now ✅
    def can_join(self):
        from datetime import timedelta
        import os
        now = timezone.now()

        is_debug = os.getenv("DEBUG", "False").lower() in {
            "1", "true", "yes"
        }

        if is_debug:
            window = timedelta(hours=48)
            return (
                self.status in [
                    ConsultationStatus.SCHEDULED,
                    ConsultationStatus.CONNECTING,
                    ConsultationStatus.ACTIVE,
                ]
                and self.scheduled_at - window <= now <= self.scheduled_at + window
            )

        before_window = timedelta(minutes=15)
        after_window = timedelta(minutes=60)
        return (
            self.status in [
                ConsultationStatus.SCHEDULED,
                ConsultationStatus.CONNECTING,
                ConsultationStatus.ACTIVE,
            ]
            and self.scheduled_at - before_window <= now
            and now <= self.scheduled_at + after_window
        )


class ConsultationNote(models.Model):
    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name="note"
    )
    doctor_notes = models.TextField(blank=True, default="")
    diagnosis = models.TextField(blank=True, default="")
    prescription = models.TextField(blank=True, default="")
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "consultation_notes"

    def __str__(self):
        return f"Notes for {self.consultation}"
    
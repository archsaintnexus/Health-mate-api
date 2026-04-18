import uuid
from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField
from accounts.models import CompanyUser

class ConsultationStatus(models.TextChoices):
    SCHEDULED  = "scheduled",  "Scheduled"
    CONNECTING = "connecting", "Connecting"
    ACTIVE     = "active",     "Active"
    COMPLETED  = "completed",  "Completed"
    CANCELLED  = "cancelled",  "Cancelled"
    MISSED     = "missed",     "Missed"


class ConsultationType(models.TextChoices):
    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"
    CHAT  = "chat",  "Chat"


class OnboardingStatus(models.TextChoices):
    INCOMPLETE = "incomplete", "Incomplete"
    PENDING    = "pending",    "Pending"
    APPROVED   = "approved",   "Approved"
    REJECTED   = "rejected",   "Rejected"


class DayOfWeek(models.TextChoices):
    MONDAY    = "monday",    "Monday"
    TUESDAY   = "tuesday",   "Tuesday"
    WEDNESDAY = "wednesday", "Wednesday"
    THURSDAY  = "thursday",  "Thursday"
    FRIDAY    = "friday",    "Friday"
    SATURDAY  = "saturday",  "Saturday"
    SUNDAY    = "sunday",    "Sunday"


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        CompanyUser,
        on_delete=models.CASCADE,
        related_name="doctor_profile"
    )

    phone_number    = models.CharField(max_length=20, blank=True, default="")
    date_of_birth   = models.DateField(null=True, blank=True)
    gender          = models.CharField(max_length=20, blank=True, default="")
    city            = models.CharField(max_length=100, blank=True, default="")
    location        = models.CharField(max_length=200, blank=True, default="")
    profile_picture = CloudinaryField(
        "consultation/doctors/avatars",
        blank=True,
        null=True,
        transformation={
            "width":   300,
            "height":  300,
            "crop":    "thumb",
            "gravity": "face",
            "quality": "auto",
        }
    )

    specialty          = models.CharField(max_length=100, blank=True, default="")
    bio                = models.TextField(blank=True, default="")
    clinical_expertise = models.TextField(blank=True, default="")
    languages          = models.CharField(max_length=200, blank=True, default="English")
    education          = models.TextField(blank=True, default="")
    experience_years   = models.PositiveIntegerField(default=0)
    consultation_type  = models.CharField(
        max_length=10,
        choices=ConsultationType.choices,
        default=ConsultationType.VIDEO
    )

    medical_school          = models.CharField(max_length=200, blank=True, default="")
    graduation_year         = models.PositiveIntegerField(null=True, blank=True)
    residency               = models.CharField(max_length=200, blank=True, default="")
    board_certifications    = models.TextField(blank=True, default="")
    professional_memberships= models.TextField(blank=True, default="")

    rating        = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    is_available  = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctor_profiles"
        ordering = ["-rating"]

    def __str__(self):
        return f"Dr. {self.user.full_name} — {self.specialty}"

class DoctorAvailability(models.Model):
    doctor      = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="availability"
    )
    day_of_week = models.CharField(
        max_length=10,
        choices=DayOfWeek.choices,
    )
    start_time  = models.TimeField()
    end_time    = models.TimeField()
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table        = "consultation_doctor_availability"
        unique_together = ("doctor", "day_of_week")
        ordering        = ["day_of_week", "start_time"]

    def __str__(self):
        return f"Dr.{self.doctor.user.full_name} — {self.day_of_week} {self.start_time}-{self.end_time}"

class DoctorDocument(models.Model):
    doctor = models.OneToOneField(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    medical_license = CloudinaryField(
        "consultation/doctors/documents/licenses",
        blank=True,
        null=True,
        transformation={
            "quality":      "auto",
            "fetch_format": "auto",
        }
    )
    medical_license_number  = models.CharField(max_length=100, blank=True, default="")
    medical_license_expiry  = models.DateField(null=True, blank=True)

    medical_certificate = CloudinaryField(
        "consultation/doctors/documents/certificates",
        blank=True,
        null=True,
        transformation={
            "quality":      "auto",
            "fetch_format": "auto",
        }
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctor_documents"

    def __str__(self):
        return f"Documents — Dr.{self.doctor.user.full_name}"

class DoctorOnboarding(models.Model):
    doctor = models.OneToOneField(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="onboarding"
    )
    status = models.CharField(
        max_length=20,
        choices=OnboardingStatus.choices,
        default=OnboardingStatus.INCOMPLETE,
    )

    step_personal_done     = models.BooleanField(default=False) 
    step_professional_done = models.BooleanField(default=False)  
    step_medical_done      = models.BooleanField(default=False)  
    step_availability_done = models.BooleanField(default=False)  
    step_documents_done    = models.BooleanField(default=False)  
    rejection_reason = models.TextField(blank=True, default="")
    reviewed_by      = models.ForeignKey(
        CompanyUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_onboardings"
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at  = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctor_onboarding"

    def __str__(self):
        return f"Onboarding — Dr.{self.doctor.user.full_name} [{self.status}]"

    @property
    def current_step(self):
        """Returns the next incomplete step number."""
        if not self.step_personal_done:     return 1
        if not self.step_professional_done: return 2
        if not self.step_medical_done:      return 3
        if not self.step_availability_done: return 4
        if not self.step_documents_done:    return 5
        return None 

    @property
    def is_complete(self):
        return all([
            self.step_personal_done,
            self.step_professional_done,
            self.step_medical_done,
            self.step_availability_done,
            self.step_documents_done,
        ])

    @property
    def can_access_dashboard(self):
        """
        Doctor can only access dashboard
        when status is approved.
        """
        return self.status == OnboardingStatus.APPROVED


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

    room_name     = models.CharField(max_length=200, blank=True, default="")
    room_url      = models.URLField(blank=True, default="")
    patient_token = models.TextField(blank=True, default="")
    doctor_token  = models.TextField(blank=True, default="")

    scheduled_at     = models.DateTimeField()
    started_at       = models.DateTimeField(null=True, blank=True)
    ended_at         = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)

    reason        = models.TextField(blank=True, default="")
    patient_notes = models.TextField(blank=True, default="")
    is_paid       = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

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

    @property
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

        before_window = timedelta(minutes=2)
        after_window  = timedelta(minutes=60)
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
    doctor_notes        = models.TextField(blank=True, default="")
    diagnosis           = models.TextField(blank=True, default="")
    prescription        = models.TextField(blank=True, default="")
    follow_up_required  = models.BooleanField(default=False)
    follow_up_date      = models.DateField(null=True, blank=True)
    is_reviewed         = models.BooleanField(default=False)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "consultation_notes"

    def __str__(self):
        return f"Notes for {self.consultation}"
    
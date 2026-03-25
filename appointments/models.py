from django.db import models
from django.utils import timezone
from accounts.models import CompanyUser
from consultation.models import DoctorProfile


class AppointmentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"
    RESCHEDULED = "rescheduled", "Rescheduled"
    NO_SHOW = "no_show", "No Show"


class ConsultationMode(models.TextChoices):
    IN_PERSON = "in_person", "In Person"
    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"


class DayOfWeek(models.IntegerChoices):
    MONDAY = 0, "Monday"
    TUESDAY = 1, "Tuesday"
    WEDNESDAY = 2, "Wednesday"
    THURSDAY = 3, "Thursday"
    FRIDAY = 4, "Friday"
    SATURDAY = 5, "Saturday"
    SUNDAY = 6, "Sunday"


class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="availability_slots"
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    slot_duration_minutes = models.PositiveIntegerField(default=30)

    class Meta:
        db_table = "doctor_availability"
        ordering = ["day_of_week", "start_time"]
        unique_together = ["doctor", "day_of_week", "start_time"]

    def __str__(self):
        return f"Dr. {self.doctor.user.full_name} — {self.get_day_of_week_display()} {self.start_time}"


class Appointment(models.Model):
    patient = models.ForeignKey(
        CompanyUser,
        on_delete=models.CASCADE,
        related_name="patient_appointments"
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="doctor_appointments"
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    consultation_mode = models.CharField(
        max_length=20,
        choices=ConsultationMode.choices,
        default=ConsultationMode.IN_PERSON
    )
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING
    )
    reason = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    cancelled_by = models.ForeignKey(
        CompanyUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cancelled_appointments"
    )
    cancellation_reason = models.TextField(blank=True, default="")
    rescheduled_from = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rescheduled_to"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "appointments"
        ordering = ["-appointment_date", "-appointment_time"]

    def __str__(self):
        return f"{self.patient.full_name} → Dr. {self.doctor.user.full_name} [{self.appointment_date}]"

    @property
    def is_upcoming(self):
        from datetime import datetime
        appointment_datetime = datetime.combine(
            self.appointment_date,
            self.appointment_time
        )
        return (
            self.status in [
                AppointmentStatus.PENDING,
                AppointmentStatus.CONFIRMED
            ]
            and appointment_datetime > datetime.now()
        )
    
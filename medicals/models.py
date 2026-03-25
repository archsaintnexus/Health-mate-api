from django.db import models
from django.utils import timezone
from accounts.models import CompanyUser
from consultation.models import DoctorProfile, Consultation


class RecordType(models.TextChoices):
    CONSULTATION_REPORT = "consultation_report", "Consultation Report"
    LAB_RESULT = "lab_result", "Lab Result"
    PRESCRIPTION = "prescription", "Prescription"
    PHYSICAL_EXAM = "physical_exam", "Physical Examination"
    IMAGING = "imaging", "Imaging/Scan"
    OTHER = "other", "Other"


class LabTestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SCHEDULED = "scheduled", "Scheduled"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"

class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        CompanyUser,
        on_delete=models.CASCADE,
        related_name="medical_records"
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_records"
    )
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medical_records"
    )
    record_type = models.CharField(
        max_length=30,
        choices=RecordType.choices,
        default=RecordType.CONSULTATION_REPORT
    )
    title = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now)
    chief_complaint = models.TextField(blank=True, default="")
    diagnosis = models.TextField(blank=True, default="")
    detailed_notes = models.TextField(blank=True, default="")
    file_url = models.URLField(blank=True, default="")
    is_downloadable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medical_records"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.patient.full_name} — {self.title} [{self.date}]"

class VitalSigns(models.Model):
    medical_record = models.OneToOneField(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name="vital_signs"
    )
    blood_pressure_systolic = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Systolic BP in mmHg e.g. 126"
    )
    blood_pressure_diastolic = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Diastolic BP in mmHg e.g. 82"
    )
    heart_rate = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Heart rate in bpm"
    )
    temperature = models.DecimalField(
        max_digits=4, decimal_places=1,
        null=True, blank=True,
        help_text="Body temperature in Fahrenheit"
    )
    oxygen_saturation = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Oxygen saturation percentage"
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=1,
        null=True, blank=True,
        help_text="Weight in kg"
    )
    height = models.DecimalField(
        max_digits=5, decimal_places=1,
        null=True, blank=True,
        help_text="Height in cm"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vital_signs"

    def __str__(self):
        return f"Vitals for {self.medical_record}"

    @property
    def blood_pressure(self):
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None

    @property
    def bmi(self):
        if self.weight and self.height:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 1)
        return None

class Prescription(models.Model):
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100, blank=True, default="")
    instructions = models.TextField(blank=True, default="")
    is_sent_to_pharmacy = models.BooleanField(default=False)
    sent_to_pharmacy_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "prescriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.medication_name} — {self.dosage}"

class LabTest(models.Model):
    patient = models.ForeignKey(
        CompanyUser,
        on_delete=models.CASCADE,
        related_name="lab_tests"
    )
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lab_tests"
    )
    ordered_by = models.ForeignKey(
        DoctorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordered_lab_tests"
    )
    test_name = models.CharField(max_length=200)
    test_description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=LabTestStatus.choices,
        default=LabTestStatus.PENDING
    )
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    result_summary = models.TextField(blank=True, default="")
    result_url = models.URLField(blank=True, default="")
    lab_name = models.CharField(max_length=200, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lab_tests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.test_name} — {self.patient.full_name} [{self.status}]"

class CarePlan(models.Model):
    medical_record = models.OneToOneField(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name="care_plan"
    )
    steps = models.JSONField(default=list, blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "care_plans"

    def __str__(self):
        return f"Care Plan for {self.medical_record}"
    
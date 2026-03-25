from django.contrib import admin
from .models import (
    MedicalRecord,
    VitalSigns,
    Prescription,
    LabTest,
    CarePlan,
)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = [
        "patient", "title", "record_type",
        "date", "doctor", "created_at"
    ]
    list_filter = ["record_type", "date"]
    search_fields = [
        "patient__email", "patient__full_name",
        "title", "diagnosis"
    ]


@admin.register(VitalSigns)
class VitalSignsAdmin(admin.ModelAdmin):
    list_display = [
        "medical_record", "blood_pressure_systolic",
        "blood_pressure_diastolic", "heart_rate",
        "temperature", "oxygen_saturation"
    ]


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = [
        "medication_name", "dosage", "frequency",
        "is_sent_to_pharmacy", "created_at"
    ]
    list_filter = ["is_sent_to_pharmacy"]
    search_fields = ["medication_name"]


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = [
        "test_name", "patient", "status",
        "scheduled_date", "completed_date"
    ]
    list_filter = ["status"]
    search_fields = ["test_name", "patient__email"]


@admin.register(CarePlan)
class CarePlanAdmin(admin.ModelAdmin):
    list_display = [
        "medical_record", "follow_up_required",
        "follow_up_date", "created_at"
    ]
    list_filter = ["follow_up_required"]
    
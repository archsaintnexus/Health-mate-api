from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import (
    MedicalRecord,
    VitalSigns,
    Prescription,
    LabTest,
    CarePlan,
    RecordType,
    LabTestStatus,
)
from consultation.serializers import DoctorProfileSerializer



class VitalSignsSerializer(serializers.ModelSerializer):
    blood_pressure = serializers.CharField(read_only=True)
    bmi = serializers.FloatField(read_only=True)

    class Meta:
        model = VitalSigns
        fields = [
            "id",
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "blood_pressure",
            "heart_rate",
            "temperature",
            "oxygen_saturation",
            "weight",
            "height",
            "bmi",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = [
            "id",
            "medication_name",
            "dosage",
            "frequency",
            "duration",
            "instructions",
            "is_sent_to_pharmacy",
            "sent_to_pharmacy_at",
            "created_at",
        ]
        read_only_fields = [
            "id", "is_sent_to_pharmacy",
            "sent_to_pharmacy_at", "created_at"
        ]

class CarePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarePlan
        fields = [
            "id",
            "steps",
            "follow_up_required",
            "follow_up_date",
            "follow_up_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LabTestSerializer(serializers.ModelSerializer):
    ordered_by_name = serializers.CharField(
        source="ordered_by.user.full_name",
        read_only=True
    )

    class Meta:
        model = LabTest
        fields = [
            "id",
            "test_name",
            "test_description",
            "status",
            "scheduled_date",
            "completed_date",
            "result_summary",
            "result_url",
            "lab_name",
            "notes",
            "ordered_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CreateLabTestSerializer(serializers.Serializer):
    test_name = serializers.CharField(max_length=200)
    test_description = serializers.CharField(
        required=False, allow_blank=True
    )
    scheduled_date = serializers.DateField(required=False, allow_null=True)
    lab_name = serializers.CharField(
        required=False, allow_blank=True, max_length=200
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    medical_record_id = serializers.IntegerField(required=False, allow_null=True)


class UpdateLabTestSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=LabTestStatus.choices,
        required=False
    )
    scheduled_date = serializers.DateField(required=False, allow_null=True)
    completed_date = serializers.DateField(required=False, allow_null=True)
    result_summary = serializers.CharField(required=False, allow_blank=True)
    result_url = serializers.URLField(required=False, allow_blank=True)
    lab_name = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class MedicalRecordSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileSerializer(read_only=True)
    vital_signs = VitalSignsSerializer(read_only=True)
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    lab_tests = LabTestSerializer(many=True, read_only=True)
    care_plan = CarePlanSerializer(read_only=True)
    patient_name = serializers.CharField(
        source="patient.full_name", read_only=True
    )

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "patient_name",
            "doctor",
            "record_type",
            "title",
            "date",
            "chief_complaint",
            "diagnosis",
            "detailed_notes",
            "file_url",
            "is_downloadable",
            "vital_signs",
            "prescriptions",
            "lab_tests",
            "care_plan",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MedicalRecordListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""
    doctor_name = serializers.CharField(
        source="doctor.user.full_name",
        read_only=True
    )
    prescription_count = serializers.SerializerMethodField()
    lab_test_count = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "record_type",
            "title",
            "date",
            "doctor_name",
            "diagnosis",
            "file_url",
            "is_downloadable",
            "prescription_count",
            "lab_test_count",
            "created_at",
        ]

    @extend_schema_field(serializers.IntegerField)
    def get_prescription_count(self, obj) -> int:
        return obj.prescriptions.count()

    @extend_schema_field(serializers.IntegerField)
    def get_lab_test_count(self, obj) -> int:
        return obj.lab_tests.count()


class CreateMedicalRecordSerializer(serializers.Serializer):
    record_type = serializers.ChoiceField(
        choices=RecordType.choices,
        default=RecordType.CONSULTATION_REPORT
    )
    title = serializers.CharField(max_length=255)
    date = serializers.DateField(required=False)
    chief_complaint = serializers.CharField(
        required=False, allow_blank=True
    )
    diagnosis = serializers.CharField(required=False, allow_blank=True)
    detailed_notes = serializers.CharField(required=False, allow_blank=True)
    file_url = serializers.URLField(required=False, allow_blank=True)
    doctor_id = serializers.IntegerField(required=False, allow_null=True)
    consultation_id = serializers.IntegerField(
        required=False, allow_null=True
    )


    vital_signs = VitalSignsSerializer(required=False)
    prescriptions = PrescriptionSerializer(many=True, required=False)
    care_plan = CarePlanSerializer(required=False)

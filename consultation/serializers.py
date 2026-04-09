from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Consultation, ConsultationNote, DoctorProfile, ConsultationStatus
from django.utils import timezone
from datetime import timedelta

from .models import (
    DoctorAvailability,
    DoctorDocument,
    DoctorOnboarding,
    DoctorProfile,
)


class DoctorProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            "id",
            "full_name",
            "email",
            "specialty",
            "bio",
            "clinical_expertise",
            "languages",
            "education",
            "experience_years",
            "consultation_type",
            "rating",
            "total_reviews",
            "is_available",
            "location",
        ]


class ConsultationNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationNote
        fields = [
            "id",
            "doctor_notes",
            "diagnosis",
            "prescription",
            "follow_up_required",
            "follow_up_date",
            "is_reviewed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConsultationSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileSerializer(read_only=True)
    note = ConsultationNoteSerializer(read_only=True)
    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )
    is_upcoming = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()

    class Meta:
        model = Consultation
        fields = [
            "id",
            "patient_name",
            "doctor",
            "consultation_type",
            "status",
            "room_url",
            "scheduled_at",
            "started_at",
            "ended_at",
            "duration_minutes",
            "reason",
            "is_upcoming",
            "can_join",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "status", "room_url",
            "started_at", "ended_at",
            "duration_minutes", "created_at", "updated_at"
        ]

    @extend_schema_field(serializers.BooleanField)
    def get_is_upcoming(self, obj) -> bool:
        return obj.is_upcoming

    @extend_schema_field(serializers.BooleanField)
    def get_can_join(self, obj) -> bool:
        return obj.can_join


class ConsultationListSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.user.full_name", read_only=True)
    doctor_specialty = serializers.CharField(source="doctor.specialty", read_only=True)
    is_upcoming = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()

    class Meta:
        model = Consultation
        fields = [
            "id",
            "doctor_name",
            "doctor_specialty",
            "status",
            "consultation_type",
            "scheduled_at",
            "duration_minutes",
            "is_upcoming",
            "can_join",
        ]

    @extend_schema_field(serializers.BooleanField)
    def get_is_upcoming(self, obj) -> bool:
        return obj.scheduled_at > timezone.now()

    @extend_schema_field(serializers.BooleanField)
    def get_can_join(self, obj) -> bool:
        now = timezone.now()
        window_start = obj.scheduled_at - timedelta(minutes=15)
        window_end = obj.scheduled_at + timedelta(minutes=60)
        return (
            window_start <= now <= window_end
            and obj.status not in [ConsultationStatus.COMPLETED, ConsultationStatus.CANCELLED]
        )


class CreateConsultationSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    consultation_type = serializers.ChoiceField(
        choices=Consultation._meta.get_field("consultation_type").choices,
        default="video"
    )
    scheduled_at = serializers.DateTimeField()
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate_doctor_id(self, value):
        from .models import DoctorProfile
        if not DoctorProfile.objects.filter(id=value, is_available=True).exists():
            raise serializers.ValidationError("Doctor not found or not available.")
        return value

    def validate_scheduled_at(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future."
            )
        return value


class JoinConsultationSerializer(serializers.Serializer):
    """Returns room details for joining a consultation."""
    room_url = serializers.URLField()
    token = serializers.CharField()
    consultation_id = serializers.IntegerField()
    doctor = DoctorProfileSerializer()
    status = serializers.CharField()


class NotesSerializer(serializers.Serializer):
    doctor_notes = serializers.CharField()
    diagnosis = serializers.CharField()
    prescription = serializers.CharField(required=False, allow_blank=True)
    follow_up_required = serializers.BooleanField(default=False)
    follow_up_date = serializers.DateField(required=False, allow_null=True)


AddConsultationNoteSerializer = NotesSerializer

class OnboardingPersonalSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    date_of_birth = serializers.DateField()
    gender = serializers.ChoiceField(choices=["Male", "Female", "Other"])
    city = serializers.CharField(max_length=100)
    location = serializers.CharField(max_length=200)
    profile_picture = serializers.ImageField(required=False)

class OnboardingProfessionalSerializer(serializers.Serializer):
    specialty = serializers.CharField(max_length=100)
    bio = serializers.CharField()
    clinical_expertise = serializers.CharField()
    languages = serializers.CharField(max_length=200)
    education = serializers.CharField()
    experience_years = serializers.IntegerField(min_value=0)
    consultation_type = serializers.ChoiceField(
        choices=["video", "audio", "chat"]
    )

class OnboardingMedicalInfoSerializer(serializers.Serializer):
    medical_school = serializers.CharField(max_length=200)
    graduation_year = serializers.IntegerField()
    residency = serializers.CharField(max_length=200, required=False, allow_blank=True)
    board_certifications = serializers.CharField(required=False, allow_blank=True)
    professional_memberships = serializers.CharField(required=False, allow_blank=True)

class AvailabilitySlotSerializer(serializers.Serializer):
    day_of_week = serializers.ChoiceField(choices=[
        "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday"
    ])
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    def validate(self, data):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "start_time must be before end_time."
            )
        return data


class OnboardingAvailabilitySerializer(serializers.Serializer):
    slots = AvailabilitySlotSerializer(many=True, min_length=1)

class OnboardingDocumentsSerializer(serializers.Serializer):
    medical_license = serializers.ImageField()
    medical_certificate = serializers.ImageField()
    medical_license_number = serializers.CharField(max_length=100, required=False)
    medical_license_expiry = serializers.DateField(required=False)

class OnboardingStatusSerializer(serializers.ModelSerializer):
    can_access_dashboard = serializers.BooleanField(read_only=True)
    current_step = serializers.IntegerField(read_only=True)

    class Meta:
        model = DoctorOnboarding
        fields = [
            "status",
            "current_step",
            "can_access_dashboard",
            "step_personal_done",
            "step_professional_done",
            "step_medical_done",
            "step_availability_done",
            "step_documents_done",
            "rejection_reason",
            "submitted_at",
            "reviewed_at",
        ]
    
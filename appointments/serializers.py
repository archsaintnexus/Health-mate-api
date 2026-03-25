from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, date
from .models import Appointment, DoctorAvailability, AppointmentStatus
from consultation.models import DoctorProfile
from consultation.serializers import DoctorProfileSerializer


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(
        source="get_day_of_week_display",
        read_only=True
    )

    class Meta:
        model = DoctorAvailability
        fields = [
            "id",
            "day_of_week",
            "day_name",
            "start_time",
            "end_time",
            "is_available",
            "slot_duration_minutes",
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileSerializer(read_only=True)
    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True
    )
    is_upcoming = serializers.BooleanField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient_name",
            "doctor",
            "appointment_date",
            "appointment_time",
            "consultation_mode",
            "status",
            "reason",
            "notes",
            "cancellation_reason",
            "is_upcoming",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "status", "created_at", "updated_at"
        ]


class BookAppointmentSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    appointment_date = serializers.DateField()
    appointment_time = serializers.TimeField()
    consultation_mode = serializers.ChoiceField(
        choices=["in_person", "video", "audio"],
        default="in_person"
    )
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate_doctor_id(self, value):
        if not DoctorProfile.objects.filter(
            id=value, is_available=True
        ).exists():
            raise serializers.ValidationError(
                "Doctor not found or not available."
            )
        return value

    def validate_appointment_date(self, value):
        if value < date.today():
            raise serializers.ValidationError(
                "Appointment date must be in the future."
            )
        return value

    def validate(self, attrs):
        # Check appointment is not in the past
        appointment_datetime = datetime.combine(
            attrs["appointment_date"],
            attrs["appointment_time"]
        )
        if appointment_datetime <= datetime.now():
            raise serializers.ValidationError(
                "Appointment date and time must be in the future."
            )

        # Check doctor has no existing appointment at same time
        doctor_id = attrs["doctor_id"]
        existing = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=attrs["appointment_date"],
            appointment_time=attrs["appointment_time"],
            status__in=[
                AppointmentStatus.PENDING,
                AppointmentStatus.CONFIRMED
            ]
        ).exists()
        if existing:
            raise serializers.ValidationError(
                "This time slot is already booked. Please choose another."
            )
        return attrs


class CancelAppointmentSerializer(serializers.Serializer):
    cancellation_reason = serializers.CharField(
        required=False,
        allow_blank=True
    )


class RescheduleAppointmentSerializer(serializers.Serializer):
    appointment_date = serializers.DateField()
    appointment_time = serializers.TimeField()

    def validate_appointment_date(self, value):
        if value < date.today():
            raise serializers.ValidationError(
                "Appointment date must be in the future."
            )
        return value
    
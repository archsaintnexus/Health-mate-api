from datetime import datetime

from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from helper.response import CustomResponse
from consultation.models import Consultation, DoctorProfile
from consultation.services import ConsultationService
from consultation.serializers import DoctorProfileSerializer
from .models import Appointment, AppointmentStatus
from .permissions import IsAppointmentParticipant, IsAppointmentPatient
from .serializers import (
    AppointmentSerializer,
    BookAppointmentSerializer,
    CancelAppointmentSerializer,
    DoctorAvailabilitySerializer,
    RescheduleAppointmentSerializer,
)
from .services import AppointmentService


# ── Doctor Views ─────────────────────────────────────────────────────────────

@extend_schema(tags=["Appointments"])
class DoctorListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="appointments_doctors_list",
        responses={200: DoctorProfileSerializer(many=True)},
        description="List all available doctors with filters.",
        tags=["Appointments"],
    )
    def get(self, request):
        doctors = DoctorProfile.objects.filter(
            is_available=True
        ).select_related("user")

        # Filters from Figma
        specialty = request.query_params.get("specialty")
        location = request.query_params.get("location")
        consultation_type = request.query_params.get("consultation_type")
        search = request.query_params.get("search")

        if specialty:
            doctors = doctors.filter(specialty__icontains=specialty)
        if location:
            doctors = doctors.filter(location__icontains=location)
        if consultation_type:
            doctors = doctors.filter(consultation_type=consultation_type)
        if search:
            doctors = doctors.filter(
                user__full_name__icontains=search
            )

        serializer = DoctorProfileSerializer(doctors, many=True)
        return CustomResponse(
            True,
            "Doctors retrieved successfully.",
            200,
            serializer.data,
        )


@extend_schema(tags=["Appointments"])
class DoctorDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="appointments_doctors_detail",
        responses={200: DoctorProfileSerializer},
        description="Get full doctor profile — Desktop 21 in Figma.",
        tags=["Appointments"],
    )
    def get(self, request, pk):
        doctor = DoctorProfile.objects.filter(
            pk=pk
        ).select_related("user").first()

        if not doctor:
            return CustomResponse(False, "Doctor not found.", 404)

        serializer = DoctorProfileSerializer(doctor)
        return CustomResponse(
            True,
            "Doctor profile retrieved.",
            200,
            serializer.data,
        )


@extend_schema(tags=["Appointments"])
class DoctorAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(description="Available slots retrieved.")},
        description="Get available time slots for a doctor on a specific date.",
        tags=["Appointments"],
    )
    def get(self, request, pk):
        doctor = DoctorProfile.objects.filter(pk=pk).first()
        if not doctor:
            return CustomResponse(False, "Doctor not found.", 404)

        date_str = request.query_params.get("date")
        if not date_str:
            return CustomResponse(
                False, "Date parameter is required. Format: YYYY-MM-DD", 400
            )

        try:
            from datetime import date
            appointment_date = date.fromisoformat(date_str)
        except ValueError:
            return CustomResponse(
                False, "Invalid date format. Use YYYY-MM-DD", 400
            )

        slots = AppointmentService.get_available_slots(doctor, appointment_date)

        return CustomResponse(
            True,
            "Available slots retrieved.",
            200,
            {
                "date": date_str,
                "doctor": DoctorProfileSerializer(doctor).data,
                "available_slots": [
                    str(slot) for slot in slots
                ],
            },
        )


# ── Appointment Views ────────────────────────────────────────────────────────

@extend_schema(tags=["Appointments"])
class AppointmentListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="appointments_list",
        responses={200: AppointmentSerializer(many=True)},
        description="List all appointments for authenticated user.",
        tags=["Appointments"],
    )
    def get(self, request):
        user = request.user

        if hasattr(user, "doctor_profile"):
            appointments = Appointment.objects.filter(
                doctor=user.doctor_profile
            ).select_related("patient", "doctor__user")
        else:
            appointments = Appointment.objects.filter(
                patient=user
            ).select_related("doctor__user")

        # Filter by status
        status = request.query_params.get("status")
        if status:
            appointments = appointments.filter(status=status)

        serializer = AppointmentSerializer(appointments, many=True)
        return CustomResponse(
            True,
            "Appointments retrieved successfully.",
            200,
            serializer.data,
        )


@extend_schema(tags=["Appointments"])
class BookAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=BookAppointmentSerializer,
        responses={
            201: OpenApiResponse(description="Appointment booked."),
            400: OpenApiResponse(description="Validation error"),
        },
        description="Book an appointment — Desktop 22 in Figma.",
        tags=["Appointments"],
    )
    @transaction.atomic
    def post(self, request):
        serializer = BookAppointmentSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(
                False, "Validation error", 400, serializer.errors
            )

        doctor = DoctorProfile.objects.get(
            id=serializer.validated_data["doctor_id"]
        )

        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=serializer.validated_data["appointment_date"],
            appointment_time=serializer.validated_data["appointment_time"],
            consultation_mode=serializer.validated_data["consultation_mode"],
            reason=serializer.validated_data.get("reason", ""),
            status=AppointmentStatus.CONFIRMED,
        )

        return CustomResponse(
            True,
            "Appointment booked successfully.",
            201,
            AppointmentSerializer(appointment).data,
        )


@extend_schema(tags=["Appointments"])
class AppointmentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAppointmentParticipant]

    @extend_schema(
        operation_id="appointments_detail",
        responses={200: AppointmentSerializer},
        description="Get appointment details.",
        tags=["Appointments"],
    )
    def get(self, request, pk):
        appointment = Appointment.objects.filter(
            pk=pk
        ).select_related("patient", "doctor__user").first()

        if not appointment:
            return CustomResponse(False, "Appointment not found.", 404)

        self.check_object_permissions(request, appointment)
        serializer = AppointmentSerializer(appointment)
        return CustomResponse(
            True,
            "Appointment retrieved successfully.",
            200,
            serializer.data,
        )


@extend_schema(tags=["Appointments"])
class JoinAppointmentConsultationView(APIView):
    permission_classes = [IsAuthenticated, IsAppointmentParticipant]

    @extend_schema(
        operation_id="appointments_join_consultation",
        request=None,
        responses={200: OpenApiResponse(description="Consultation join data returned.")},
        description=(
            "Create or fetch consultation for an appointment and return "
            "Daily room_url + token for the authenticated participant."
        ),
        tags=["Appointments"],
    )
    @transaction.atomic
    def post(self, request, pk):
        appointment = Appointment.objects.filter(
            pk=pk
        ).select_related("patient", "doctor__user").first()
        if not appointment:
            return CustomResponse(False, "Appointment not found.", 404)

        self.check_object_permissions(request, appointment)

        if appointment.status not in [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
        ]:
            return CustomResponse(
                False,
                "Only pending or confirmed appointments can join consultation.",
                400,
            )

        if appointment.consultation_mode == "in_person":
            return CustomResponse(
                False,
                "In-person appointments cannot be joined via Daily.",
                400,
            )

        scheduled_at = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time,
        )
        if timezone.is_naive(scheduled_at):
            scheduled_at = timezone.make_aware(
                scheduled_at,
                timezone.get_current_timezone(),
            )

        consultation = Consultation.objects.filter(
            patient=appointment.patient,
            doctor=appointment.doctor,
            scheduled_at=scheduled_at,
        ).first()

        if not consultation:
            consultation = Consultation.objects.create(
                patient=appointment.patient,
                doctor=appointment.doctor,
                consultation_type=appointment.consultation_mode,
                scheduled_at=scheduled_at,
                reason=appointment.reason,
                is_paid=True,
            )

        try:
            join_payload = ConsultationService.join_consultation(
                consultation=consultation,
                user=request.user,
            )
        except Exception as e:
            print("❌ JOIN ERROR:", str(e))
            return CustomResponse(False, str(e), 400)

        return CustomResponse(
            True,
            "Appointment consultation join data returned.",
            200,
            {
                "appointment_id": appointment.id,
                **join_payload,
            },
        )


@extend_schema(tags=["Appointments"])
class CancelAppointmentView(APIView):
    permission_classes = [IsAuthenticated, IsAppointmentParticipant]

    @extend_schema(
        request=CancelAppointmentSerializer,
        responses={200: OpenApiResponse(description="Appointment cancelled successfully.")},
        description="Cancel an appointment.",
        tags=["Appointments"],
    )
    def post(self, request, pk):
        appointment = Appointment.objects.filter(pk=pk).first()
        if not appointment:
            return CustomResponse(False, "Appointment not found.", 404)

        self.check_object_permissions(request, appointment)

        if appointment.status not in [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
        ]:
            return CustomResponse(
                False,
                "Only pending or confirmed appointments can be cancelled.",
                400,
            )

        serializer = CancelAppointmentSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(
                False, "Validation error", 400, serializer.errors
            )

        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancelled_by = request.user
        appointment.cancellation_reason = serializer.validated_data.get(
            "cancellation_reason", ""
        )
        appointment.save(update_fields=[
            "status", "cancelled_by", "cancellation_reason"
        ])

        return CustomResponse(
            True, "Appointment cancelled successfully.", 200
        )


@extend_schema(tags=["Appointments"])
class RescheduleAppointmentView(APIView):
    permission_classes = [IsAuthenticated, IsAppointmentParticipant]

    @extend_schema(
        request=RescheduleAppointmentSerializer,
        responses={201: AppointmentSerializer},
        description="Reschedule an appointment.",
        tags=["Appointments"],
    )
    @transaction.atomic
    def post(self, request, pk):
        appointment = Appointment.objects.filter(pk=pk).first()
        if not appointment:
            return CustomResponse(False, "Appointment not found.", 404)

        self.check_object_permissions(request, appointment)

        if appointment.status not in [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
        ]:
            return CustomResponse(
                False,
                "Only pending or confirmed appointments can be rescheduled.",
                400,
            )

        serializer = RescheduleAppointmentSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(
                False, "Validation error", 400, serializer.errors
            )

        # Create new appointment
        new_appointment = Appointment.objects.create(
            patient=appointment.patient,
            doctor=appointment.doctor,
            appointment_date=serializer.validated_data["appointment_date"],
            appointment_time=serializer.validated_data["appointment_time"],
            consultation_mode=appointment.consultation_mode,
            reason=appointment.reason,
            status=AppointmentStatus.CONFIRMED,
            rescheduled_from=appointment,
        )

        # Cancel old appointment
        appointment.status = AppointmentStatus.RESCHEDULED
        appointment.save(update_fields=["status"])

        return CustomResponse(
            True,
            "Appointment rescheduled successfully.",
            201,
            AppointmentSerializer(new_appointment).data,
        )
    
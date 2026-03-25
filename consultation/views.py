from django.utils import timezone
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from helper.response import CustomResponse
from .models import (
    Consultation,
    ConsultationNote,
    ConsultationStatus,
    DoctorProfile,
)
from .permissions import (
    IsConsultationDoctor,
    IsConsultationParticipant,
    IsDoctor,
    IsPatient,
)
from .serializers import (
    AddConsultationNoteSerializer,
    ConsultationSerializer,
    CreateConsultationSerializer,
    DoctorProfileSerializer,
)
from .services import DailyCoService


# ── Doctor Views ─────────────────────────────────────────────────────────────

class DoctorListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="consultation_doctors_list",
        responses={200: DoctorProfileSerializer(many=True)},
        description="List all available doctors with optional filters.",
        tags=["Consultation"],
    )
    def get(self, request):
        doctors = DoctorProfile.objects.filter(is_available=True).select_related("user")

        # Filters
        specialty = request.query_params.get("specialty")
        location = request.query_params.get("location")
        consultation_type = request.query_params.get("consultation_type")

        if specialty:
            doctors = doctors.filter(specialty__icontains=specialty)
        if location:
            doctors = doctors.filter(location__icontains=location)
        if consultation_type:
            doctors = doctors.filter(consultation_type=consultation_type)

        serializer = DoctorProfileSerializer(doctors, many=True)
        return CustomResponse(
            True,
            "Doctors retrieved successfully.",
            200,
            serializer.data,
        )


class DoctorDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="consultation_doctors_detail",
        responses={200: DoctorProfileSerializer},
        description="Get a doctor's full profile.",
        tags=["Consultation"],
    )
    def get(self, request, pk):
        doctor = DoctorProfile.objects.filter(pk=pk).select_related("user").first()
        if not doctor:
            return CustomResponse(False, "Doctor not found.", 404)

        serializer = DoctorProfileSerializer(doctor)
        return CustomResponse(
            True,
            "Doctor profile retrieved successfully.",
            200,
            serializer.data,
        )


# ── Consultation Views ───────────────────────────────────────────────────────

class ConsultationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="consultation_list",
        responses={200: ConsultationSerializer(many=True)},
        description="List all consultations for the authenticated user.",
        tags=["Consultation"],
    )
    def get(self, request):
        user = request.user

        # Doctors see their consultations, patients see theirs
        if hasattr(user, "doctor_profile"):
            consultations = Consultation.objects.filter(
                doctor=user.doctor_profile
            ).select_related("patient", "doctor__user")
        else:
            consultations = Consultation.objects.filter(
                patient=user
            ).select_related("doctor__user")

        serializer = ConsultationSerializer(consultations, many=True)
        return CustomResponse(
            True,
            "Consultations retrieved successfully.",
            200,
            serializer.data,
        )

    @extend_schema(
        request=CreateConsultationSerializer,
        responses={
            201: OpenApiResponse(description="Consultation booked successfully."),
            400: OpenApiResponse(description="Validation error"),
        },
        description="Book a new consultation with a doctor.",
        tags=["Consultation"],
    )
    @transaction.atomic
    def post(self, request):
        serializer = CreateConsultationSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        doctor = DoctorProfile.objects.get(
            id=serializer.validated_data["doctor_id"]
        )

        consultation = Consultation.objects.create(
            patient=request.user,
            doctor=doctor,
            consultation_type=serializer.validated_data["consultation_type"],
            scheduled_at=serializer.validated_data["scheduled_at"],
            reason=serializer.validated_data.get("reason", ""),
            status=ConsultationStatus.SCHEDULED,
        )

        return CustomResponse(
            True,
            "Consultation booked successfully.",
            201,
            ConsultationSerializer(consultation).data,
        )


class ConsultationDetailView(APIView):
    permission_classes = [IsAuthenticated, IsConsultationParticipant]

    @extend_schema(
        operation_id="consultation_detail",
        responses={200: ConsultationSerializer},
        description="Get consultation details.",
        tags=["Consultation"],
    )
    def get(self, request, pk):
        consultation = Consultation.objects.filter(pk=pk).select_related(
            "patient", "doctor__user"
        ).first()

        if not consultation:
            return CustomResponse(False, "Consultation not found.", 404)

        self.check_object_permissions(request, consultation)
        serializer = ConsultationSerializer(consultation)
        return CustomResponse(
            True,
            "Consultation retrieved successfully.",
            200,
            serializer.data,
        )


class JoinConsultationView(APIView):
    permission_classes = [IsAuthenticated, IsConsultationParticipant]

    @extend_schema(
        request=None,
        description="Join a consultation — returns Daily.co room URL and token.",
        tags=["Consultation"],
        responses={
            200: OpenApiResponse(description="Room URL and token returned."),
            400: OpenApiResponse(description="Cannot join consultation."),
        }
    )
    @transaction.atomic
    def post(self, request, pk):
        consultation = Consultation.objects.filter(pk=pk).select_related(
            "patient", "doctor__user"
        ).first()

        if not consultation:
            return CustomResponse(False, "Consultation not found.", 404)

        self.check_object_permissions(request, consultation)

        if not consultation.can_join:
            return CustomResponse(
                False,
                "This consultation cannot be joined at this time.",
                400,
            )

        # Create Daily.co room if not exists
        if not consultation.room_url:
            try:
                room_data = DailyCoService.setup_consultation_room(consultation)
                consultation.room_name = room_data["room_name"]
                consultation.room_url = room_data["room_url"]
                consultation.patient_token = room_data["patient_token"]
                consultation.doctor_token = room_data["doctor_token"]
                consultation.status = ConsultationStatus.CONNECTING
                consultation.save()
            except Exception as e:
                return CustomResponse(
                    False,
                    "Failed to create consultation room. Try again.",
                    502,
                )

        # Return correct token based on who is joining
        is_doctor = hasattr(request.user, "doctor_profile")
        token = consultation.doctor_token if is_doctor else consultation.patient_token

        return CustomResponse(
            True,
            "Joining consultation.",
            200,
            {
                "consultation_id": consultation.id,
                "room_url": consultation.room_url,
                "token": token,
                "status": consultation.status,
                "doctor": DoctorProfileSerializer(consultation.doctor).data,
                "scheduled_at": consultation.scheduled_at,
            },
        )


class StartConsultationView(APIView):
    permission_classes = [IsAuthenticated, IsConsultationParticipant]

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Consultation started.")},
        description="Mark consultation as active when call starts.",
        tags=["Consultation"],
    )
    def post(self, request, pk):
        consultation = Consultation.objects.filter(pk=pk).first()
        if not consultation:
            return CustomResponse(False, "Consultation not found.", 404)

        self.check_object_permissions(request, consultation)

        consultation.status = ConsultationStatus.ACTIVE
        consultation.started_at = timezone.now()
        consultation.save(update_fields=["status", "started_at"])

        return CustomResponse(True, "Consultation started.", 200)


class EndConsultationView(APIView):
    permission_classes = [IsAuthenticated, IsConsultationParticipant]

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Consultation ended successfully.")},
        description="End a consultation and calculate duration.",
        tags=["Consultation"],
    )
    @transaction.atomic
    def post(self, request, pk):
        consultation = Consultation.objects.filter(pk=pk).first()
        if not consultation:
            return CustomResponse(False, "Consultation not found.", 404)

        self.check_object_permissions(request, consultation)

        if consultation.status != ConsultationStatus.ACTIVE:
            return CustomResponse(
                False, "Consultation is not active.", 400
            )

        # Calculate duration
        ended_at = timezone.now()
        duration = 0
        if consultation.started_at:
            delta = ended_at - consultation.started_at
            duration = int(delta.total_seconds() / 60)

        consultation.status = ConsultationStatus.COMPLETED
        consultation.ended_at = ended_at
        consultation.duration_minutes = duration
        consultation.save(update_fields=[
            "status", "ended_at", "duration_minutes"
        ])

        # Delete Daily.co room
        if consultation.room_name:
            DailyCoService.delete_room(consultation.room_name)

        return CustomResponse(
            True,
            "Consultation ended successfully.",
            200,
            {
                "duration_minutes": duration,
                "status": consultation.status,
            },
        )


class CancelConsultationView(APIView):
    permission_classes = [IsAuthenticated, IsConsultationParticipant]

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Consultation cancelled.")},
        description="Cancel a scheduled consultation.",
        tags=["Consultation"],
    )
    def post(self, request, pk):
        consultation = Consultation.objects.filter(pk=pk).first()
        if not consultation:
            return CustomResponse(False, "Consultation not found.", 404)

        self.check_object_permissions(request, consultation)

        if consultation.status not in [
            ConsultationStatus.SCHEDULED,
            ConsultationStatus.CONNECTING,
        ]:
            return CustomResponse(
                False,
                "Only scheduled consultations can be cancelled.",
                400,
            )

        consultation.status = ConsultationStatus.CANCELLED
        consultation.save(update_fields=["status"])

        # Delete Daily.co room if exists
        if consultation.room_name:
            DailyCoService.delete_room(consultation.room_name)

        return CustomResponse(True, "Consultation cancelled.", 200)


class AddConsultationNoteView(APIView):
    permission_classes = [IsAuthenticated, IsConsultationDoctor]

    @extend_schema(
        request=AddConsultationNoteSerializer,
        responses={200: OpenApiResponse(description="Consultation notes saved successfully.")},
        description="Doctor adds notes after consultation ends.",
        tags=["Consultation"],
    )
    def post(self, request, pk):
        consultation = Consultation.objects.filter(pk=pk).first()
        if not consultation:
            return CustomResponse(False, "Consultation not found.", 404)

        self.check_object_permissions(request, consultation)

        if consultation.status != ConsultationStatus.COMPLETED:
            return CustomResponse(
                False,
                "Notes can only be added to completed consultations.",
                400,
            )

        serializer = AddConsultationNoteSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        note, created = ConsultationNote.objects.update_or_create(
            consultation=consultation,
            defaults=serializer.validated_data,
        )

        return CustomResponse(
            True,
            "Consultation notes saved successfully.",
            200,
            {
                "doctor_notes": note.doctor_notes,
                "diagnosis": note.diagnosis,
                "prescription": note.prescription,
                "follow_up_required": note.follow_up_required,
                "follow_up_date": note.follow_up_date,
            },
        )
    
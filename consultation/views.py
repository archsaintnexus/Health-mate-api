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
    NotesSerializer,
    ConsultationListSerializer,
    ConsultationSerializer,
    CreateConsultationSerializer,
    DoctorProfileSerializer,
)
from .services import ConsultationService


# ── Consultation Views ───────────────────────────────────────────────────────

@extend_schema(tags=["Consultation"])
class ConsultationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="consultation_list",
        responses={200: ConsultationListSerializer(many=True)},
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

        serializer = ConsultationListSerializer(consultations, many=True)
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


@extend_schema(tags=["Consultation"])
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


@extend_schema(tags=["Consultation"])
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

        try:
            join_payload = ConsultationService.join_consultation(
                consultation=consultation,
                user=request.user,
            )
        except Exception as e:
            return CustomResponse(False, str(e), 400)

        return CustomResponse(
            True,
            "Joining consultation.",
            200,
            {
                **join_payload,
                "doctor": DoctorProfileSerializer(consultation.doctor).data,
            },
        )


@extend_schema(tags=["Consultation"])
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


@extend_schema(tags=["Consultation"])
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
            from .services import DailyCoService
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


@extend_schema(tags=["Consultation"])
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
            from .services import DailyCoService
            DailyCoService.delete_room(consultation.room_name)

        return CustomResponse(True, "Consultation cancelled.", 200)


@extend_schema(tags=["Consultation"])
class AddConsultationNoteView(APIView):
    permission_classes = [IsAuthenticated, IsConsultationDoctor]

    @extend_schema(
        request=NotesSerializer,
        responses={200: OpenApiResponse(description="Consultation notes saved successfully.")},
        description="Doctor adds notes after consultation ends.",
        tags=["Consultation"],
    )
    def post(self, request, pk):
        consultation = Consultation.objects.filter(pk=pk).first()
        if not consultation:
            return CustomResponse(False, "Consultation not found.", 404)

        self.check_object_permissions(request, consultation)

        serializer = NotesSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        try:
            consultation, note = ConsultationService.add_notes(
                consultation_id=pk,
                doctor=request.user,
                data=serializer.validated_data,
            )
        except Exception as e:
            return CustomResponse(False, str(e), 400)

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
    
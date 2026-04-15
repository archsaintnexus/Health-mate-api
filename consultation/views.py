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
    DoctorOnboarding,
    DoctorProfile,
    OnboardingStatus,
)
from .permissions import (
    IsApprovedDoctor,
    IsConsultationDoctor,
    IsConsultationParticipant,
    IsDoctor,
    IsPatient,
    IsProviderUser,
)
from .serializers import (
    OnboardingAvailabilitySerializer,
    OnboardingDocumentsSerializer,
    OnboardingMedicalInfoSerializer,
    OnboardingPersonalSerializer,
    OnboardingProfessionalSerializer,
    OnboardingStatusSerializer,
    NotesSerializer,
    ConsultationListSerializer,
    ConsultationSerializer,
    CreateConsultationSerializer,
    DoctorProfileSerializer,
)
from .services import ConsultationService, OnboardingService

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

@extend_schema(tags=["Consultation"])
class OnboardingPersonalView(APIView):
    permission_classes = [IsAuthenticated, IsProviderUser]

    @extend_schema(
        request=OnboardingPersonalSerializer,
        responses={200: OpenApiResponse(description="Personal info saved.")},
        description="Step 1 — Save doctor personal information.",
        tags=["Consultation"],
    )
    def post(self, request):
        serializer = OnboardingPersonalSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        try:
            OnboardingService.save_personal_info(
                user=request.user,
                data=serializer.validated_data,
            )
        except Exception as e:
            return CustomResponse(False, str(e), 400)

        return CustomResponse(
            True,
            "Personal information saved successfully.",
            200,
            {"next_step": 2},
        )

@extend_schema(tags=["Consultation"])
class OnboardingProfessionalView(APIView):
    permission_classes = [IsAuthenticated, IsProviderUser]

    @extend_schema(
        request=OnboardingProfessionalSerializer,
        responses={200: OpenApiResponse(description="Professional details saved.")},
        description="Step 2 — Save doctor professional details.",
        tags=["Consultation"],
    )
    def post(self, request):
        serializer = OnboardingProfessionalSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        try:
            OnboardingService.save_professional_info(
                user=request.user,
                data=serializer.validated_data,
            )
        except Exception as e:
            return CustomResponse(False, str(e), 400)

        return CustomResponse(
            True,
            "Professional details saved successfully.",
            200,
            {"next_step": 3},
        )
@extend_schema(tags=["Consultation"])
class OnboardingMedicalInfoView(APIView):
    permission_classes = [IsAuthenticated, IsProviderUser]

    @extend_schema(
        request=OnboardingMedicalInfoSerializer,
        responses={200: OpenApiResponse(description="Medical info saved.")},
        description="Step 3 — Save chief medical information.",
        tags=["Consultation"],
    )
    def post(self, request):
        serializer = OnboardingMedicalInfoSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        try:
            OnboardingService.save_medical_info(
                user=request.user,
                data=serializer.validated_data,
            )
        except Exception as e:
            return CustomResponse(False, str(e), 400)

        return CustomResponse(
            True,
            "Medical information saved successfully.",
            200,
            {"next_step": 4},
        )

@extend_schema(tags=["Consultation"])
class OnboardingAvailabilityView(APIView):
    permission_classes = [IsAuthenticated, IsProviderUser]

    @extend_schema(
        request=OnboardingAvailabilitySerializer,
        responses={200: OpenApiResponse(description="Availability saved.")},
        description="Step 4 — Set doctor availability schedule.",
        tags=["Consultation"],
    )
    def post(self, request):
        serializer = OnboardingAvailabilitySerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        try:
            OnboardingService.save_availability(
                user=request.user,
                slots=serializer.validated_data["slots"],
            )
        except Exception as e:
            return CustomResponse(False, str(e), 400)

        return CustomResponse(
            True,
            "Availability saved successfully.",
            200,
            {"next_step": 5},
        )

@extend_schema(tags=["Consultation"])
class OnboardingDocumentsView(APIView):
    permission_classes = [IsAuthenticated, IsProviderUser]

    @extend_schema(
        request=OnboardingDocumentsSerializer,
        responses={
            200: OpenApiResponse(description="Documents uploaded. Status: pending."),
        },
        description="Step 5 (Final) — Upload medical license and certificate. Sets status to pending.",
        tags=["Consultation"],
    )
    def post(self, request):
        serializer = OnboardingDocumentsSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        try:
            OnboardingService.save_documents(
                user=request.user,
                data=serializer.validated_data,
            )
        except Exception as e:
            return CustomResponse(False, str(e), 400)

        return CustomResponse(
            True,
            "Documents uploaded successfully. Your application is under review.",
            200,
            {
                "status": "pending",
                "can_access_dashboard": False,
                "message": "Review typically takes 1-3 business days.",
            },
        )

@extend_schema(tags=["Consultation"])
class OnboardingStatusView(APIView):
    permission_classes = [IsAuthenticated, IsProviderUser]

    @extend_schema(
        responses={200: OpenApiResponse(description="Onboarding status returned.")},
        description="Get current onboarding status and step progress.",
        tags=["Consultation"],
    )
    def get(self, request):
        try:
            status_data = OnboardingService.get_status(request.user)
        except Exception as e:
            return CustomResponse(False, str(e), 400)

        return CustomResponse(
            True,
            "Onboarding status retrieved.",
            200,
            status_data,
        )

@extend_schema(tags=["Consultation"])
class OnboardingResubmitView(APIView):
    permission_classes = [IsAuthenticated, IsProviderUser]

    @extend_schema(
        request=OnboardingDocumentsSerializer,
        responses={
            200: OpenApiResponse(description="Documents resubmitted. Status: pending."),
            400: OpenApiResponse(description="Only rejected applications can be resubmitted."),
        },
        description="Resubmit documents after rejection.",
        tags=["Consultation"],
    )
    def post(self, request):
        serializer = OnboardingDocumentsSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        try:
            OnboardingService.resubmit(
                user=request.user,
                data=serializer.validated_data,
            )
        except ValueError as e:
            return CustomResponse(False, str(e), 400)
        except Exception as e:
            return CustomResponse(False, str(e), 400)

        return CustomResponse(
            True,
            "Documents resubmitted. Your application is under review.",
            200,
            {
                "status": "pending",
                "can_access_dashboard": False,
                "message": "Review typically takes 1-3 business days.",
            },
        )

@extend_schema(tags=["Consultation"])
class DoctorListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: DoctorProfileSerializer(many=True)},
        description="List all approved doctors.",
        tags=["Consultation"],
    )
    def get(self, request):
        doctors = DoctorProfile.objects.filter(
            onboarding__status="approved"
        ).select_related("user")
        return CustomResponse(
            True,
            "Doctors retrieved successfully.",
            200,
            DoctorProfileSerializer(doctors, many=True).data,
        )


@extend_schema(tags=["Consultation"])
class DoctorDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: DoctorProfileSerializer},
        description="Get a single doctor's profile.",
        tags=["Consultation"],
    )
    def get(self, request, pk):
        doctor = DoctorProfile.objects.filter(
            pk=pk,
            onboarding__status="approved"
        ).select_related("user").first()

        if not doctor:
            return CustomResponse(False, "Doctor not found.", 404)

        return CustomResponse(
            True,
            "Doctor profile retrieved successfully.",
            200,
            DoctorProfileSerializer(doctor).data,
        )
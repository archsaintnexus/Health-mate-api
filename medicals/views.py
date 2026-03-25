from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from helper.response import CustomResponse
from consultation.models import DoctorProfile
from .models import MedicalRecord, LabTest, Prescription, LabTestStatus
from .permissions import (
    IsMedicalRecordOwner,
    IsLabTestOwner,
    IsPatientOrDoctor,
)
from .serializers import (
    CreateLabTestSerializer,
    CreateMedicalRecordSerializer,
    LabTestSerializer,
    MedicalRecordListSerializer,
    MedicalRecordSerializer,
    UpdateLabTestSerializer,
)
from .services import MedicalRecordService


# ── Medical Record Views ──────────────────────────────────────────────────────

class MedicalRecordListView(APIView):
    permission_classes = [IsAuthenticated, IsPatientOrDoctor]

    @extend_schema(
        operation_id="medicals_records_list",
        responses={200: MedicalRecordListSerializer(many=True)},
        description="List all medical records for authenticated user.",
        tags=["Medical Records"],
    )
    def get(self, request):
        user = request.user

        # Doctors see records they created
        # Patients see their own records
        if hasattr(user, "doctor_profile"):
            records = MedicalRecord.objects.filter(
                doctor=user.doctor_profile
            ).select_related("patient", "doctor__user")
        else:
            records = MedicalRecord.objects.filter(
                patient=user
            ).select_related("doctor__user")

        # Filter by record type
        record_type = request.query_params.get("record_type")
        if record_type:
            records = records.filter(record_type=record_type)

        # Filter by date range
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        if date_from:
            records = records.filter(date__gte=date_from)
        if date_to:
            records = records.filter(date__lte=date_to)

        serializer = MedicalRecordListSerializer(records, many=True)
        return CustomResponse(
            True,
            "Medical records retrieved successfully.",
            200,
            serializer.data,
        )

    @extend_schema(
        request=CreateMedicalRecordSerializer,
        responses={
            201: OpenApiResponse(description="Medical record created."),
            400: OpenApiResponse(description="Validation error"),
        },
        description="Create a new medical record.",
        tags=["Medical Records"],
    )
    @transaction.atomic
    def post(self, request):
        serializer = CreateMedicalRecordSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(
                False, "Validation error", 400, serializer.errors
            )

        data = serializer.validated_data

        # Get doctor if provided
        doctor = None
        doctor_id = data.pop("doctor_id", None)
        if doctor_id:
            doctor = DoctorProfile.objects.filter(
                id=doctor_id
            ).first()

        # Get consultation if provided
        consultation = None
        consultation_id = data.pop("consultation_id", None)
        if consultation_id:
            from consultation.models import Consultation
            consultation = Consultation.objects.filter(
                id=consultation_id
            ).first()

        record = MedicalRecordService.create_full_record(
            patient=request.user,
            validated_data=data,
            doctor=doctor,
            consultation=consultation,
        )

        return CustomResponse(
            True,
            "Medical record created successfully.",
            201,
            MedicalRecordSerializer(record).data,
        )


class MedicalRecordDetailView(APIView):
    permission_classes = [IsAuthenticated, IsMedicalRecordOwner]

    @extend_schema(
        operation_id="medicals_records_detail",
        responses={200: MedicalRecordSerializer},
        description="Get medical record detail.",
        tags=["Medical Records"],
    )
    def get(self, request, pk):
        record = MedicalRecord.objects.filter(
            pk=pk
        ).select_related(
            "patient", "doctor__user", "consultation"
        ).prefetch_related(
            "vital_signs", "prescriptions",
            "lab_tests", "care_plan"
        ).first()

        if not record:
            return CustomResponse(
                False, "Medical record not found.", 404
            )

        self.check_object_permissions(request, record)
        serializer = MedicalRecordSerializer(record)
        return CustomResponse(
            True,
            "Medical record retrieved successfully.",
            200,
            serializer.data,
        )


class SendPrescriptionToPharmacyView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Prescription sent to pharmacy successfully.")},
        description="Send prescription to pharmacy.",
        tags=["Medical Records"],
    )
    def post(self, request, pk, prescription_id):
        record = MedicalRecord.objects.filter(pk=pk).first()
        if not record:
            return CustomResponse(
                False, "Medical record not found.", 404
            )

        if record.patient != request.user:
            return CustomResponse(
                False, "Permission denied.", 403
            )

        prescription = Prescription.objects.filter(
            id=prescription_id,
            medical_record=record
        ).first()

        if not prescription:
            return CustomResponse(
                False, "Prescription not found.", 404
            )

        if prescription.is_sent_to_pharmacy:
            return CustomResponse(
                False,
                "Prescription already sent to pharmacy.",
                400
            )

        success = MedicalRecordService.send_prescription_to_pharmacy(
            prescription
        )

        if success:
            return CustomResponse(
                True,
                "Prescription sent to pharmacy successfully.",
                200,
            )
        return CustomResponse(
            False, "Failed to send prescription.", 500
        )


# ── Lab Test Views ────────────────────────────────────────────────────────────

class LabTestListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="medicals_lab_tests_list",
        responses={200: LabTestSerializer(many=True)},
        description="List all lab tests for authenticated user.",
        tags=["Lab Tests"],
    )
    def get(self, request):
        user = request.user

        if hasattr(user, "doctor_profile"):
            lab_tests = LabTest.objects.filter(
                ordered_by=user.doctor_profile
            ).select_related("patient", "ordered_by__user")
        else:
            lab_tests = LabTest.objects.filter(
                patient=user
            ).select_related("ordered_by__user")

        # Filter by status
        status = request.query_params.get("status")
        if status:
            lab_tests = lab_tests.filter(status=status)

        serializer = LabTestSerializer(lab_tests, many=True)
        return CustomResponse(
            True,
            "Lab tests retrieved successfully.",
            200,
            serializer.data,
        )

    @extend_schema(
        request=CreateLabTestSerializer,
        responses={201: LabTestSerializer},
        description="Book a new lab test.",
        tags=["Lab Tests"],
    )
    @transaction.atomic
    def post(self, request):
        serializer = CreateLabTestSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(
                False, "Validation error", 400, serializer.errors
            )

        data = serializer.validated_data
        medical_record_id = data.pop("medical_record_id", None)

        medical_record = None
        if medical_record_id:
            medical_record = MedicalRecord.objects.filter(
                id=medical_record_id,
                patient=request.user
            ).first()

        lab_test = LabTest.objects.create(
            patient=request.user,
            medical_record=medical_record,
            **data
        )

        return CustomResponse(
            True,
            "Lab test booked successfully.",
            201,
            LabTestSerializer(lab_test).data,
        )


class LabTestDetailView(APIView):
    permission_classes = [IsAuthenticated, IsLabTestOwner]

    @extend_schema(
        operation_id="medicals_lab_tests_detail",
        responses={200: LabTestSerializer},
        description="Get lab test detail.",
        tags=["Lab Tests"],
    )
    def get(self, request, pk):
        lab_test = LabTest.objects.filter(
            pk=pk
        ).select_related(
            "patient", "ordered_by__user", "medical_record"
        ).first()

        if not lab_test:
            return CustomResponse(False, "Lab test not found.", 404)

        self.check_object_permissions(request, lab_test)
        serializer = LabTestSerializer(lab_test)
        return CustomResponse(
            True,
            "Lab test retrieved successfully.",
            200,
            serializer.data,
        )

    @extend_schema(
        request=UpdateLabTestSerializer,
        responses={200: LabTestSerializer},
        description="Update lab test status or results.",
        tags=["Lab Tests"],
    )
    def patch(self, request, pk):
        lab_test = LabTest.objects.filter(pk=pk).first()
        if not lab_test:
            return CustomResponse(False, "Lab test not found.", 404)

        self.check_object_permissions(request, lab_test)

        serializer = UpdateLabTestSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(
                False, "Validation error", 400, serializer.errors
            )

        for field, value in serializer.validated_data.items():
            setattr(lab_test, field, value)
        lab_test.save()

        return CustomResponse(
            True,
            "Lab test updated successfully.",
            200,
            LabTestSerializer(lab_test).data,
        )
    
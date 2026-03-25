import logging
from django.utils import timezone
from .models import (
    MedicalRecord,
    VitalSigns,
    Prescription,
    CarePlan,
    LabTest,
    LabTestStatus,
)

logger = logging.getLogger(__name__)


class MedicalRecordService:

    @staticmethod
    def create_full_record(
        patient,
        validated_data: dict,
        doctor=None,
        consultation=None,
    ) -> MedicalRecord:
        """
        Create a medical record with optional
        vital signs, prescriptions and care plan.
        """
        vital_signs_data = validated_data.pop("vital_signs", None)
        prescriptions_data = validated_data.pop("prescriptions", [])
        care_plan_data = validated_data.pop("care_plan", None)

        # Create medical record
        record = MedicalRecord.objects.create(
            patient=patient,
            doctor=doctor,
            consultation=consultation,
            **validated_data,
        )

        # Create vital signs
        if vital_signs_data:
            VitalSigns.objects.create(
                medical_record=record,
                **vital_signs_data
            )

        # Create prescriptions
        for prescription in prescriptions_data:
            Prescription.objects.create(
                medical_record=record,
                **prescription
            )

        # Create care plan
        if care_plan_data:
            CarePlan.objects.create(
                medical_record=record,
                **care_plan_data
            )

        logger.info(
            f"Medical record created: {record.id} "
            f"for patient: {patient.email}"
        )
        return record

    @staticmethod
    def send_prescription_to_pharmacy(prescription) -> bool:
        """Mark prescription as sent to pharmacy."""
        try:
            prescription.is_sent_to_pharmacy = True
            prescription.sent_to_pharmacy_at = timezone.now()
            prescription.save(update_fields=[
                "is_sent_to_pharmacy",
                "sent_to_pharmacy_at"
            ])
            logger.info(
                f"Prescription {prescription.id} "
                f"sent to pharmacy"
            )
            return True
        except Exception as e:
            logger.error(
                f"Failed to send prescription to pharmacy: {e}"
            )
            return False
        
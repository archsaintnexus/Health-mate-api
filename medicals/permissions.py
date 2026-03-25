from rest_framework.permissions import BasePermission
from accounts.models import UserRole


class IsPatientOrDoctor(BasePermission):
    """Only patients and doctors can access medical records."""
    message = "You must be a patient or doctor to access medical records."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in [
                UserRole.PATIENT,
                UserRole.PROVIDER,
                UserRole.ADMIN,
            ]
        )


class IsMedicalRecordOwner(BasePermission):
    """Only the patient or doctor of the record can access it."""
    message = "You do not have permission to access this medical record."

    def has_object_permission(self, request, view, obj):
        return (
            obj.patient == request.user
            or (
                obj.doctor
                and obj.doctor.user == request.user
            )
            or request.user.role == UserRole.ADMIN
        )


class IsLabTestOwner(BasePermission):
    """Only the patient who owns the lab test can access it."""
    message = "You do not have permission to access this lab test."

    def has_object_permission(self, request, view, obj):
        return (
            obj.patient == request.user
            or (
                obj.ordered_by
                and obj.ordered_by.user == request.user
            )
            or request.user.role == UserRole.ADMIN
        )


class IsDoctor(BasePermission):
    """Only doctors can create/update medical records."""
    message = "Only doctors can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.PROVIDER
        )
    
from rest_framework.permissions import BasePermission
from accounts.models import UserRole
from consultation.models import OnboardingStatus


class IsDoctor(BasePermission):
    """Only users with doctor role can access."""
    message = "You must be a doctor to perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.PROVIDER
        )


class IsPatient(BasePermission):
    """Only users with patient role can access."""
    message = "You must be a patient to perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.PATIENT
        )


class IsConsultationParticipant(BasePermission):
    """Only the patient or doctor of a consultation can access it."""
    message = "You are not a participant of this consultation."

    def has_object_permission(self, request, view, obj):
        return (
            obj.patient == request.user
            or obj.doctor.user == request.user
        )


class IsConsultationDoctor(BasePermission):
    """Only the doctor of a consultation can access it."""
    message = "You are not the doctor for this consultation."

    def has_object_permission(self, request, view, obj):
        return obj.doctor.user == request.user


class IsApprovedDoctor(BasePermission):
    """
    Only approved doctors can access
    doctor-specific endpoints.
    """
    message = "Your account is pending admin approval."

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if not hasattr(user, "doctor_profile"):
            return False
        onboarding = getattr(user.doctor_profile, "onboarding", None)
        if not onboarding:
            return False
        return onboarding.status == "approved"


class IsProviderUser(BasePermission):
    """
    Only users with role=provider can access
    onboarding endpoints.
    """
    message = "Only medical professionals can access this."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "provider"
        )
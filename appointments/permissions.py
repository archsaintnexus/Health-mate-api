from rest_framework.permissions import BasePermission
from accounts.models import UserRole


class IsAppointmentParticipant(BasePermission):
    """Only patient or doctor of appointment can access."""
    message = "You are not a participant of this appointment."

    def has_object_permission(self, request, view, obj):
        return (
            obj.patient == request.user
            or obj.doctor.user == request.user
        )


class IsAppointmentPatient(BasePermission):
    """Only the patient of the appointment can access."""
    message = "You are not the patient for this appointment."

    def has_object_permission(self, request, view, obj):
        return obj.patient == request.user
    
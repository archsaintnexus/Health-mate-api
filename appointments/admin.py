from django.contrib import admin
from .models import Appointment, DoctorAvailability


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = [
        "doctor", "day_of_week",
        "start_time", "end_time",
        "is_available", "slot_duration_minutes"
    ]
    list_filter = ["day_of_week", "is_available"]
    search_fields = ["doctor__user__email", "doctor__user__full_name"]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "patient", "doctor", "appointment_date",
        "appointment_time", "status", "consultation_mode"
    ]
    list_filter = ["status", "consultation_mode", "appointment_date"]
    search_fields = [
        "patient__email", "doctor__user__email"
    ]
    
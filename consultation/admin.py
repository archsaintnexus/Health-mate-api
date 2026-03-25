from django.contrib import admin
from .models import Consultation, ConsultationNote, DoctorProfile


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user", "specialty", "rating",
        "is_available", "experience_years"
    ]
    list_filter = ["specialty", "is_available", "consultation_type"]
    search_fields = ["user__email", "user__full_name", "specialty"]


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = [
        "patient", "doctor", "status",
        "consultation_type", "scheduled_at", "duration_minutes"
    ]
    list_filter = ["status", "consultation_type"]
    search_fields = [
        "patient__email", "doctor__user__email"
    ]


@admin.register(ConsultationNote)
class ConsultationNoteAdmin(admin.ModelAdmin):
    list_display = [
        "consultation", "follow_up_required", "follow_up_date"
    ]
    search_fields = ["consultation__patient__email"]
    
from django.contrib import admin
from django.utils import timezone
from .models import (
    DoctorProfile, DoctorOnboarding,
    DoctorAvailability, DoctorDocument,
    Consultation, ConsultationNote,
)
from helper.tasks import send_a_mail


@admin.register(DoctorOnboarding)
class DoctorOnboardingAdmin(admin.ModelAdmin):
    list_display = [
        "get_doctor_name", "get_doctor_email",
        "status", "submitted_at", "reviewed_at"
    ]
    list_filter = ["status"]
    search_fields = ["doctor__user__full_name", "doctor__user__email"]
    readonly_fields = ["submitted_at", "reviewed_at"]
    actions = ["approve_doctors", "reject_doctors"]

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.full_name}"
    get_doctor_name.short_description = "Doctor"

    def get_doctor_email(self, obj):
        return obj.doctor.user.email
    get_doctor_email.short_description = "Email"

    def approve_doctors(self, request, queryset):
        for onboarding in queryset:
            onboarding.status = "approved"
            onboarding.reviewed_at = timezone.now()
            onboarding.reviewed_by = request.user
            onboarding.save(update_fields=[
                "status", "reviewed_at", "reviewed_by"
            ])
            # ✅ Send approval email
            send_a_mail.delay(
                title="Congratulations! You're Verified — Health Mate",
                message=f"""
                <html>
                  <body style="font-family: Arial, sans-serif;">
                    <h3>You're Verified! ✅</h3>
                    <p>Dear Dr. {onboarding.doctor.user.full_name},</p>
                    <p>Your application has been approved.
                    You can now access your dashboard.</p>
                    <p>Welcome to Health Mate!</p>
                  </body>
                </html>
                """,
                to=onboarding.doctor.user.email,
                is_html=True,
            )
        self.message_user(request, f"{queryset.count()} doctor(s) approved.")
    approve_doctors.short_description = "✅ Approve selected doctors"

    def reject_doctors(self, request, queryset):
        # Note: For rejection with reason, use inline editing
        for onboarding in queryset:
            onboarding.status = "rejected"
            onboarding.reviewed_at = timezone.now()
            onboarding.reviewed_by = request.user
            onboarding.save(update_fields=[
                "status", "reviewed_at", "reviewed_by"
            ])
            # ✅ Send rejection email
            send_a_mail.delay(
                title="Application Update — Health Mate",
                message=f"""
                <html>
                  <body style="font-family: Arial, sans-serif;">
                    <h3>Application Update</h3>
                    <p>Dear Dr. {onboarding.doctor.user.full_name},</p>
                    <p>Unfortunately your application was not approved.</p>
                    <p><strong>Reason:</strong> {onboarding.rejection_reason or 'Please check your documents.'}</p>
                    <p>You can log in and resubmit your documents.</p>
                  </body>
                </html>
                """,
                to=onboarding.doctor.user.email,
                is_html=True,
            )
        self.message_user(request, f"{queryset.count()} doctor(s) rejected.")
    reject_doctors.short_description = "❌ Reject selected doctors"


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "specialty", "experience_years", "is_available"]
    search_fields = ["user__full_name", "specialty"]


@admin.register(DoctorDocument)
class DoctorDocumentAdmin(admin.ModelAdmin):
    list_display = ["doctor", "medical_license_number", "uploaded_at"]


admin.site.register(DoctorAvailability)
admin.site.register(Consultation)
admin.site.register(ConsultationNote)
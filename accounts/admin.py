from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CompanyUser, OTPCode


@admin.register(CompanyUser)
class CompanyUserAdmin(UserAdmin):
    model = CompanyUser
    list_display = ("email", "full_name", "role", "is_email_verified", "is_active", "created_at")
    list_filter = ("role", "is_email_verified", "is_active", "created_at")
    search_fields = ("email", "full_name", "phone_number", "firebase_uid")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("full_name", "phone_number", "firebase_uid", "role")}),
        ("Status", {"fields": ("is_email_verified", "is_active", "is_staff", "is_superuser")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "full_name", "role", "is_active"),
            },
        ),
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose", "code", "is_used", "attempts", "expires_at", "created_at")
    list_filter = ("purpose", "is_used", "created_at")
    search_fields = ("user__email", "code")
    ordering = ("-created_at",)

from django.contrib import admin

from .models import (
    HomeCareNotification,
    HomeCareRequest,
    HomeCareService,
    HomeCareTimeSlot,
)


@admin.register(HomeCareService)
class HomeCareServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "price", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(HomeCareTimeSlot)
class HomeCareTimeSlotAdmin(admin.ModelAdmin):
    list_display = ("service", "label", "start_time", "end_time", "is_active")
    list_filter = ("service", "is_active")
    search_fields = ("label", "service__name")


@admin.register(HomeCareRequest)
class HomeCareRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "service",
        "request_date",
        "time_slot",
        "phone_number",
        "status",
        "created_at",
    )
    list_filter = ("status", "service", "request_date")
    search_fields = ("user__username", "address", "phone_number")


@admin.register(HomeCareNotification)
class HomeCareNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "title", "message")
    
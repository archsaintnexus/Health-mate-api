from django.contrib import admin
from .models import HomeCareService, HomeCareRequest, HomeCareNotification

# Register your models here.


@admin.register(HomeCareService)
class HomeCareServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(HomeCareRequest)
class HomeCareRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "service",
        "preferred_time",
        "status",
        "phone_number",
        "created_at",
    )
    list_filter = ("status", "service", "preferred_time")
    search_fields = ("user__username", "phone_number", "address")


@admin.register(HomeCareNotification)
class HomeCareNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "title", "message")
from django.contrib import admin

from .models import (
    PharmacyCategory,
    PharmacyProduct,
    PharmacyOrder,
    PharmacyOrderItem,
    PharmacyNotification,
)


@admin.register(PharmacyCategory)
class PharmacyCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PharmacyProduct)
class PharmacyProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "stock_quantity",
        "requires_prescription",
        "is_active",
    )
    list_filter = ("category", "requires_prescription", "is_active")
    search_fields = ("name", "description")


class PharmacyOrderItemInline(admin.TabularInline):
    model = PharmacyOrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price")


@admin.register(PharmacyOrder)
class PharmacyOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "total_amount",
        "phone_number",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "phone_number", "delivery_address")
    inlines = [PharmacyOrderItemInline]


@admin.register(PharmacyNotification)
class PharmacyNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "title", "message")
    
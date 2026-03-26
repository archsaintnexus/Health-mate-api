from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    OrderTrackingEvent,
    PharmacyCategory,
    PharmacyNotification,
    PharmacyOrder,
    PharmacyOrderItem,
    PharmacyProduct,
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
        "pack_size",
        "strength",
        "stock_quantity",
        "requires_prescription",
        "is_active",
    )
    list_filter = ("category", "requires_prescription", "is_active")
    search_fields = ("name", "description", "slug")
    prepopulated_fields = {"slug": ("name",)}


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    inlines = [CartItemInline]


class PharmacyOrderItemInline(admin.TabularInline):
    model = PharmacyOrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price")


class OrderTrackingEventInline(admin.TabularInline):
    model = OrderTrackingEvent
    extra = 0
    readonly_fields = ("status", "title", "note", "event_time", "created_at")


@admin.register(PharmacyOrder)
class PharmacyOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "full_name",
        "delivery_method",
        "payment_status",
        "status",
        "total_amount",
        "created_at",
    )
    list_filter = ("delivery_method", "payment_status", "status", "created_at")
    search_fields = ("order_number", "full_name", "phone_number", "email")
    inlines = [PharmacyOrderItemInline, OrderTrackingEventInline]


@admin.register(PharmacyNotification)
class PharmacyNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "title", "message")
    
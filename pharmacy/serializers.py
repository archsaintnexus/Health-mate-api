from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

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


class PharmacyCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = PharmacyCategory
        fields = ["id", "name", "slug", "image"]

    def get_image(self, obj):
        return obj.image.url if obj.image else None


class PharmacyProductSerializer(serializers.ModelSerializer):
    category = PharmacyCategorySerializer(read_only=True)
    image = serializers.SerializerMethodField()
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = PharmacyProduct
        fields = [
            "id",
            "category",
            "name",
            "image",
            "slug",
            "description",
            "price",
            "pack_size",
            "strength",
            "stock_quantity",
            "requires_prescription",
            "is_active",
            "in_stock",
        ]

    def get_image(self, obj):
        return obj.image.url if obj.image else None


class CartItemSerializer(serializers.ModelSerializer):
    product = PharmacyProductSerializer(read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "line_total", "created_at", "updated_at"]

    def get_line_total(self, obj):
        return obj.line_total


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "subtotal", "total_items", "created_at", "updated_at"]

    def get_subtotal(self, obj):
        return obj.subtotal

    def get_total_items(self, obj):
        return obj.total_items


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, attrs):
        product_id = attrs["product_id"]
        quantity = attrs["quantity"]

        try:
            product = PharmacyProduct.objects.get(id=product_id, is_active=True)
        except PharmacyProduct.DoesNotExist:
            raise serializers.ValidationError({"product_id": "Product not found."})

        if quantity > product.stock_quantity:
            raise serializers.ValidationError(
                {"quantity": f"Only {product.stock_quantity} item(s) available in stock."}
            )

        attrs["product"] = product
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        product = self.validated_data["product"]
        quantity = self.validated_data["quantity"]

        cart, _ = Cart.objects.get_or_create(user=user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                raise serializers.ValidationError(
                    {"quantity": f"Only {product.stock_quantity} item(s) available in stock."}
                )
            cart_item.quantity = new_quantity
            cart_item.save(update_fields=["quantity", "updated_at"])

        return cart


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")

        if value > self.instance.product.stock_quantity:
            raise serializers.ValidationError(
                f"Only {self.instance.product.stock_quantity} item(s) available in stock."
            )

        return value


class PharmacyOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = PharmacyOrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image",
            "quantity",
            "unit_price",
            "line_total",
        ]

    def get_product_image(self, obj):
        return obj.product.image.url if obj.product.image else None

    def get_line_total(self, obj):
        return obj.line_total


class OrderTrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTrackingEvent
        fields = ["id", "status", "title", "note", "event_time", "created_at"]


class PharmacyOrderSerializer(serializers.ModelSerializer):
    items = PharmacyOrderItemSerializer(many=True, read_only=True)
    tracking_events = OrderTrackingEventSerializer(many=True, read_only=True)

    class Meta:
        model = PharmacyOrder
        fields = [
            "id",
            "order_number",
            "full_name",
            "phone_number",
            "alternate_phone_number",
            "email",
            "delivery_method",
            "delivery_address",
            "country",
            "state",
            "order_instructions",
            "payment_status",
            "payment_reference",
            "status",
            "subtotal",
            "shipping_fee",
            "total_amount",
            "estimated_delivery_start",
            "estimated_delivery_end",
            "items",
            "tracking_events",
            "created_at",
            "updated_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=30)
    alternate_phone_number = serializers.CharField(max_length=30, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    delivery_method = serializers.ChoiceField(choices=PharmacyOrder.DeliveryMethod.choices)
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    order_instructions = serializers.CharField(required=False, allow_blank=True)
    shipping_fee = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default=Decimal("0.00")
    )

    def validate(self, attrs):
        if (
            attrs.get("delivery_method") == PharmacyOrder.DeliveryMethod.SHIP
            and not attrs.get("delivery_address")
        ):
            raise serializers.ValidationError(
                {"delivery_address": "Delivery address is required when delivery method is ship."}
            )
        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        user = self.context["request"].user

        try:
            cart = Cart.objects.prefetch_related("items__product").get(user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError({"cart": "Cart does not exist."})

        cart_items = cart.items.select_related("product").all()
        if not cart_items.exists():
            raise serializers.ValidationError({"cart": "Your cart is empty."})

        for item in cart_items:
            if not item.product.is_active:
                raise serializers.ValidationError(
                    {"cart": f"{item.product.name} is no longer available."}
                )
            if item.quantity > item.product.stock_quantity:
                raise serializers.ValidationError(
                    {"cart": f"Insufficient stock for {item.product.name}."}
                )

        order_number = f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S%f')}"
        payment_reference = f"PAY-{timezone.now().strftime('%Y%m%d%H%M%S%f')}"

        order = PharmacyOrder.objects.create(
            user=user,
            order_number=order_number,
            full_name=self.validated_data["full_name"],
            phone_number=self.validated_data["phone_number"],
            alternate_phone_number=self.validated_data.get("alternate_phone_number", ""),
            email=self.validated_data.get("email", ""),
            delivery_method=self.validated_data["delivery_method"],
            delivery_address=self.validated_data.get("delivery_address", ""),
            country=self.validated_data.get("country", ""),
            state=self.validated_data.get("state", ""),
            order_instructions=self.validated_data.get("order_instructions", ""),
            shipping_fee=self.validated_data.get("shipping_fee", Decimal("0.00")),
            payment_reference=payment_reference,
            payment_status=PharmacyOrder.PaymentStatus.PENDING,
            status=PharmacyOrder.Status.PENDING,
        )

        for item in cart_items:
            PharmacyOrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.price,
            )

        order.recalculate_total()

        OrderTrackingEvent.objects.create(
            order=order,
            status=PharmacyOrder.Status.PENDING,
            title="Order Placed",
            note="Your order has been placed successfully and is awaiting payment confirmation.",
            event_time=timezone.now(),
        )

        return order


class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyOrder
        fields = [
            "status",
            "payment_status",
            "estimated_delivery_start",
            "estimated_delivery_end",
        ]

    def update(self, instance, validated_data):
        old_status = instance.status
        instance = super().update(instance, validated_data)

        if "status" in validated_data and validated_data["status"] != old_status:
            title_map = {
                PharmacyOrder.Status.CONFIRMED: "Order Confirmed",
                PharmacyOrder.Status.PROCESSING: "Order Processing",
                PharmacyOrder.Status.OUT_FOR_DELIVERY: "Out for Delivery",
                PharmacyOrder.Status.DELIVERED: "Delivered",
                PharmacyOrder.Status.CANCELLED: "Cancelled",
            }
            OrderTrackingEvent.objects.create(
                order=instance,
                status=instance.status,
                title=title_map.get(instance.status, "Order Updated"),
                note=f"Order status changed to {instance.get_status_display()}.",
                event_time=timezone.now(),
            )

        return instance


class PharmacyNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyNotification
        fields = ["id", "title", "message", "is_read", "created_at"]
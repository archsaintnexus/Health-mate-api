from django.db import transaction
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import (
    PharmacyCategory,
    PharmacyProduct,
    PharmacyOrder,
    PharmacyOrderItem,
    PharmacyNotification,
)


class PharmacyCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = PharmacyCategory
        fields = ["id", "name", "slug", "image"]

    @extend_schema_field(serializers.URLField)
    def get_image(self, obj):
        return obj.image.url if obj.image else None


class PharmacyProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    category = PharmacyCategorySerializer(read_only=True)

    class Meta:
        model = PharmacyProduct
        fields = [
            "id",
            "category",
            "name",
            "image",
            "description",
            "price",
            "stock_quantity",
            "requires_prescription",
            "is_active",
        ]
    
    def get_image(self, obj):
        return obj.image.url if obj.image else None


class PharmacyOrderItemReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = PharmacyOrderItem
        fields = ["id", "product", "product_name", "quantity", "unit_price", "line_total"]

    def get_line_total(self, obj):
        return obj.line_total


class PharmacyOrderReadSerializer(serializers.ModelSerializer):
    items = PharmacyOrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = PharmacyOrder
        fields = [
            "id",
            "status",
            "delivery_address",
            "phone_number",
            "total_amount",
            "notes",
            "created_at",
            "items",
        ]


class PharmacyOrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class PharmacyOrderCreateSerializer(serializers.Serializer):
    delivery_address = serializers.CharField()
    phone_number = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)
    items = PharmacyOrderItemCreateSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        items_data = validated_data.pop("items")

        order = PharmacyOrder.objects.create(user=user, **validated_data)
        total_amount = 0

        for item_data in items_data:
            product_id = item_data["product_id"]
            quantity = item_data["quantity"]

            try:
                product = PharmacyProduct.objects.select_for_update().get(
                    id=product_id,
                    is_active=True
                )
            except PharmacyProduct.DoesNotExist:
                raise serializers.ValidationError(
                    {"items": f"Product with id {product_id} does not exist."}
                )

            if product.stock_quantity < quantity:
                raise serializers.ValidationError(
                    {"items": f"Insufficient stock for {product.name}."}
                )

            PharmacyOrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
            )

            product.stock_quantity -= quantity
            product.save(update_fields=["stock_quantity", "updated_at"])

            total_amount += product.price * quantity

        order.total_amount = total_amount
        order.save(update_fields=["total_amount", "updated_at"])
        return order


class PharmacyOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyOrder
        fields = ["id", "status", "updated_at"]


class PharmacyNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyNotification
        fields = ["id", "title", "message", "is_read", "created_at"]
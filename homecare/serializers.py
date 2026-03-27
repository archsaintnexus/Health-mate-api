from datetime import date

from rest_framework import serializers

from .models import (
    HomeCareNotification,
    HomeCareRequest,
    HomeCareService,
    HomeCareTimeSlot,
)


class HomeCareServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeCareService
        fields = ["id", "name", "slug", "description", "price", "is_active"]


class HomeCareTimeSlotSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = HomeCareTimeSlot
        fields = [
            "id",
            "service",
            "service_name",
            "label",
            "start_time",
            "end_time",
            "is_active",
        ]


class HomeCareRequestSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    time_slot_label = serializers.CharField(source="time_slot.label", read_only=True)

    class Meta:
        model = HomeCareRequest
        fields = [
            "id",
            "service",
            "service_name",
            "time_slot",
            "time_slot_label",
            "request_date",
            "description",
            "address",
            "phone_number",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]


class CreateHomeCareRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeCareRequest
        fields = [
            "service",
            "time_slot",
            "request_date",
            "description",
            "address",
            "phone_number",
        ]

    def validate_request_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Request date cannot be in the past.")
        return value

    def validate(self, attrs):
        service = attrs.get("service")
        time_slot = attrs.get("time_slot")

        if time_slot.service_id != service.id:
            raise serializers.ValidationError(
                {"time_slot": "Selected time slot does not belong to the selected service."}
            )

        if not time_slot.is_active:
            raise serializers.ValidationError(
                {"time_slot": "Selected time slot is not available."}
            )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        return HomeCareRequest.objects.create(
            user=request.user,
            status=HomeCareRequest.Status.PENDING,
            **validated_data
        )


class UpdateHomeCareRequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeCareRequest
        fields = ["status"]

    def validate_status(self, value):
        allowed = {
            HomeCareRequest.Status.PENDING,
            HomeCareRequest.Status.CONFIRMED,
            HomeCareRequest.Status.IN_PROGRESS,
            HomeCareRequest.Status.COMPLETED,
            HomeCareRequest.Status.CANCELLED,
        }
        if value not in allowed:
            raise serializers.ValidationError("Invalid status.")
        return value


class HomeCareNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeCareNotification
        fields = ["id", "title", "message", "is_read", "created_at"]
        